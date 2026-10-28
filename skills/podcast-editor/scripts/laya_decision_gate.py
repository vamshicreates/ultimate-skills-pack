#!/usr/bin/env python3
"""
Embedded Laya Non-Autoregressive Decision Gate (https://github.com/NandhaKishorM/laya)
for the Multi-Cam Podcast Editor Skill (`podcast-editor`).

CORE POLICY — MINIMAL TOKEN USAGE & CALL LAYA ONLY WHEN NECESSARY:
1. Basic / Explicit / Direct Tasks -> BYPASS Laya completely (`laya_called: False`) and execute
   manually using the skill's native CLI/MCP tools with zero model overhead.
2. Complex / Ambiguous Multi-Branch Multicam Editorial Routing -> Invoke Laya's `Router` in a single
   non-autoregressive forward pass (~33ms, 0 LLM tokens) using typed questions (`choice`, `score`, `noul`)
   to decide camera switching (`CU_S0`, `CU_S1`, `WIDE`), cutaway density, and J/L-cut transitions.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SKILL_NAME = "podcast-editor"
APP_LABEL = "Multi-Cam Podcast Editor (Premiere Pro & DaVinci Resolve)"
DOMAIN = "podcast_multicam"
LAYA_REPO_URL = "https://github.com/NandhaKishorM/laya"

DEFAULT_PRESET_QUESTIONS: Dict[str, Any] = {
    "camera_switch_archetype": {
        "type": "choice",
        "instructions": "Which multi-camera switching profile best fits this podcast conversation segment?",
        "criteria": {
            "active_speaker_closeup": "solo speaker delivering a clear point, story, or punchline -> frame them in their dedicated Close-Up camera",
            "wide_group_interaction": "both hosts/guests talking, laughing together, rapid back-and-forth banter, or establishing a new topic -> use the Wide two/three-shot camera",
            "reaction_cutaway_insert": "extended monologue (>16s) or emotional/humorous beat where a brief 2s reaction shot or wide reset prevents visual stagnation"
        }
    },
    "pacing_tightness": {
        "type": "score",
        "instructions": "How aggressively should silence gaps and camera switches be paced?",
        "criteria": [
            "relaxed_cinematic_podcast",
            "balanced_conversational_flow",
            "tight_high_retention_podcast"
        ]
    },
    "use_j_l_audio_lead": {
        "type": "noul",
        "instructions": "Should J-cuts and L-cuts (audio leading or trailing video by 4-10 frames) be used across speaker camera switches?",
        "criteria": {
            "true": "natural conversational podcast where overlapping audio transitions smooth out camera angle switches",
            "false": "strict hard-cut rhythmic edit where audio and video must switch on the exact same frame"
        },
        "labels": {
            "true": "A",
            "false": "B"
        }
    },
    "monologue_punch_in": {
        "type": "noul",
        "instructions": "Should a subtle 108% punch-in scale zoom be applied when staying on the same Close-Up camera across a silence cut?",
        "criteria": {
            "true": "hide same-camera jump cuts when dead air is removed inside a single speaker's monologue",
            "false": "always cut to the Wide camera instead of punching in on the same Close-Up camera"
        },
        "labels": {
            "true": "A",
            "false": "B"
        }
    }
}

BASIC_TASK_PATTERNS = [
    r"^\s*(status|ping|list|check|inspect|export|save|open|close|render|sync)\b",
    r"\b(set|change|move|scale|delete|remove|copy|add marker|cut silence)\b.*\b(to|by|at|from)\b.*(\d|true|false)",
]

COMPLEX_DECISION_INDICATORS = [
    "decide", "choose", "which camera", "which angle", "wide or closeup", "wide or close-up",
    "ambiguous", "multi-cam", "multicam", "podcast", "speaker", "crosstalk", "banter",
    "monologue", "reaction", "pacing", "strategy", "orchestrate", "edit full",
]


def should_call_laya(state_text: str, force: bool = False) -> Tuple[bool, str]:
    """
    Deterministic complexity gate that decides whether Laya is genuinely needed.
    Returns (call_laya: bool, reason: str).
    """
    if force:
        return True, "Forced via --force-laya flag."

    clean = (state_text or "").strip()
    if not clean:
        return False, "Empty state — basic manual execution."

    lower = clean.lower()
    word_count = len(clean.split())

    if word_count <= 10 and not any(k in lower for k in COMPLEX_DECISION_INDICATORS):
        return (
            False,
            f"Basic/direct task detected ({word_count} words, no multi-branch ambiguity). "
            "Bypassing Laya and executing directly.",
        )

    for pat in BASIC_TASK_PATTERNS:
        if re.search(pat, lower) and not any(k in lower for k in COMPLEX_DECISION_INDICATORS):
            return (
                False,
                "Explicit parameter/command pattern detected. Bypassing Laya and executing directly.",
            )

    matched_indicators = [k for k in COMPLEX_DECISION_INDICATORS if k in lower]
    if matched_indicators or word_count >= 18:
        return (
            True,
            f"Complex/multi-branch multicam decision detected (words={word_count}, "
            f"indicators={matched_indicators[:3]}). Calling Laya Router.",
        )

    return (
        False,
        "Standard task without multi-branch ambiguity. Bypassing Laya and executing directly.",
    )


def sanitize_questions_for_laya(questions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforce NandhaKishorM/laya best practices:
      - `noul` questions must have explicit `criteria` keyed by 'true'/'false'
        and neutral `labels: {'true': 'A', 'false': 'B'}` (Issue #156).
    """
    sanitized = {}
    for q_key, q_spec in questions.items():
        spec = dict(q_spec)
        if spec.get("type") == "noul":
            if "criteria" not in spec or not isinstance(spec["criteria"], dict):
                instr = spec.get("instructions", "Does the statement hold?")
                spec["criteria"] = {
                    "true": f"yes, {instr}",
                    "false": f"no, not ({instr})",
                }
            if "labels" not in spec:
                spec["labels"] = {"true": "A", "false": "B"}
        sanitized[q_key] = spec
    return sanitized


def heuristic_fallback_answers(state_text: str, questions: Dict[str, Any]) -> Dict[str, Any]:
    """Fast zero-overhead deterministic fallback when Laya is bypassed or not yet installed."""
    lower = (state_text or "").lower()
    answers = {}
    for q_key, q_spec in questions.items():
        q_type = q_spec.get("type", "choice")
        criteria = q_spec.get("criteria", {})
        if q_type == "choice" and isinstance(criteria, dict) and criteria:
            best_opt = next(iter(criteria.keys()))
            best_hits = -1
            for opt_k, opt_desc in criteria.items():
                words = [w for w in re.findall(r"[a-z0-9]+", f"{opt_k} {opt_desc}".lower()) if len(w) > 3]
                hits = sum(1 for w in words if w in lower)
                if hits > best_hits:
                    best_hits = hits
                    best_opt = opt_k
            answers[q_key] = {"choice": best_opt, "confidence": 0.82, "source": "direct_heuristic"}
        elif q_type == "score" and isinstance(criteria, list) and criteria:
            mid_idx = min(len(criteria) - 1, max(0, len(criteria) // 2))
            if any(w in lower for w in ("fast", "viral", "tight", "rapid")):
                mid_idx = len(criteria) - 1
            elif any(w in lower for w in ("slow", "relaxed", "cinematic")):
                mid_idx = 0
            answers[q_key] = {"score": criteria[mid_idx], "level_index": mid_idx, "confidence": 0.80, "source": "direct_heuristic"}
        elif q_type == "noul":
            answers[q_key] = {"noul": 0.72, "bool": True, "confidence": 0.78, "source": "direct_heuristic"}
    return answers


def evaluate_decision(
    state_text: str,
    questions: Dict[str, Any] = None,
    force_laya: bool = False,
    min_confidence: float = 0.55,
) -> Dict[str, Any]:
    """
    Evaluate typed decisions with strict complexity gating:
      - If `should_call_laya` is False -> returns immediately (`laya_called: False`, `execution_mode: "direct_manual_execution"`).
      - If `should_call_laya` is True  -> calls `laya.Router().predict(...)` (`laya_called: True`).
    """
    active_questions = sanitize_questions_for_laya(questions or DEFAULT_PRESET_QUESTIONS)
    call_needed, gate_reason = should_call_laya(state_text, force=force_laya)

    if not call_needed:
        return {
            "skill": SKILL_NAME,
            "domain": DOMAIN,
            "laya_called": False,
            "execution_mode": "direct_manual_execution",
            "gate_reason": gate_reason,
            "instruction": "Task is basic/explicit. Do NOT load Laya; execute the action directly using native skill tools.",
            "recommended_defaults": heuristic_fallback_answers(state_text, active_questions),
        }

    try:
        from laya import Router  # type: ignore

        router = Router()
        raw_result = router.predict(state_text, active_questions, min_confidence=min_confidence)
        return {
            "skill": SKILL_NAME,
            "domain": DOMAIN,
            "laya_called": True,
            "execution_mode": "laya_system1_router",
            "gate_reason": gate_reason,
            "routing": raw_result.get("routing", {"model": "english"}),
            "answers": raw_result.get("answers", {}),
        }
    except ImportError:
        return {
            "skill": SKILL_NAME,
            "domain": DOMAIN,
            "laya_called": False,
            "laya_installed": False,
            "execution_mode": "fallback_direct_execution",
            "gate_reason": gate_reason,
            "install_hint": "Run `python3 scripts/laya_decision_gate.py --install` or `pip install laya` to enable neural Laya routing.",
            "answers": heuristic_fallback_answers(state_text, active_questions),
        }
    except Exception as exc:
        return {
            "skill": SKILL_NAME,
            "domain": DOMAIN,
            "laya_called": False,
            "execution_mode": "fallback_after_error",
            "gate_reason": gate_reason,
            "laya_error": str(exc),
            "answers": heuristic_fallback_answers(state_text, active_questions),
        }


def decide_podcast_segment_angle(
    segment: Dict[str, Any],
    seg_index: int,
    total_segments: int,
    prev_angle: str,
    consecutive_same_angle_sec: float,
    available_roles: Dict[str, str],
    use_laya_for_ambiguous: bool = True,
) -> Dict[str, Any]:
    """
    Zero-LLM-token camera switching decision engine combining deterministic multicam rules
    with Laya System-1 routing for ambiguous beats (long monologues, emotional/laughter beats).

    Roles expected in `available_roles`:
      - "WIDE": camera_id (e.g. "Camera 3")
      - "CU_S0": camera_id (e.g. "Camera 1")
      - "CU_S1": camera_id (e.g. "Camera 2")
      - "CU_S2": optional 3rd speaker camera_id
    """
    speaker = str(segment.get("speaker", "S0"))
    text = str(segment.get("text", "")).strip()
    dur = float(segment.get("end", 0.0)) - float(segment.get("start", 0.0))
    is_crosstalk = bool(segment.get("is_crosstalk", False)) or speaker in ("BOTH", "MULTI", "ALL")
    has_laughter = any(tok in text.lower() for tok in ("(laughs)", "(laughter)", "haha", "(chuckles)", "(applause)"))

    wide_cam = available_roles.get("WIDE") or available_roles.get("CU_S0") or "Camera 1"
    cu_s0 = available_roles.get("CU_S0") or wide_cam
    cu_s1 = available_roles.get("CU_S1") or wide_cam
    cu_s2 = available_roles.get("CU_S2") or wide_cam

    # Rule 1: Opening establishment (first segment when >= 5 segments) or closing segment (>= 6 segments) -> WIDE shot
    if seg_index == 0 and total_segments >= 5 and dur >= 1.5:
        return {
            "role": "WIDE",
            "camera": wide_cam,
            "scale": 100.0,
            "beat": "ESTABLISH_OPEN",
            "reason": "Opening podcast establishing wide shot showing all speakers in frame",
            "laya_invoked": False,
        }
    if seg_index == total_segments - 1 and total_segments >= 6 and dur >= 2.0:
        return {
            "role": "WIDE",
            "camera": wide_cam,
            "scale": 100.0,
            "beat": "ESTABLISH_CLOSE",
            "reason": "Closing podcast wide shot for wrap-up",
            "laya_invoked": False,
        }

    # Rule 2: Cross-talk, shared laughter, or ultra-short rapid ping-pong (< 1.4s) -> WIDE shot
    if is_crosstalk or has_laughter or dur < 1.4:
        reason = (
            "Cross-talk / simultaneous speech -> Wide angle keeps both speakers visible"
            if is_crosstalk
            else (
                "Shared laughter / reaction beat -> Wide angle captures group chemistry"
                if has_laughter
                else f"Rapid back-and-forth turn ({dur:.2f}s < 1.4s) -> Wide shot prevents jarring ping-pong cuts"
            )
        )
        return {
            "role": "WIDE",
            "camera": wide_cam,
            "scale": 100.0,
            "beat": "INTERACTION_WIDE",
            "reason": reason,
            "laya_invoked": False,
        }

    # Map active speaker to their dedicated Close-Up camera
    if speaker in ("S0", "speaker_0", "0"):
        target_role = "CU_S0"
        target_cam = cu_s0
    elif speaker in ("S1", "speaker_1", "1"):
        target_role = "CU_S1"
        target_cam = cu_s1
    elif speaker in ("S2", "speaker_2", "2"):
        target_role = "CU_S2"
        target_cam = cu_s2
    else:
        target_role = "WIDE"
        target_cam = wide_cam

    # Rule 3: Ambiguous / Long Monologue (>= 15s on the same close-up) -> Consult Laya Decision Model
    if consecutive_same_angle_sec >= 15.0 and target_role == prev_angle:
        state_desc = (
            f"Podcast speaker {speaker} has been on {target_role} continuously for {consecutive_same_angle_sec:.1f}s. "
            f"Current phrase ({dur:.1f}s): '{text[:120]}'. Decide whether to reset to WIDE angle or punch-in on Close-Up."
        )
        if use_laya_for_ambiguous:
            laya_res = evaluate_decision(state_desc, force_laya=False)
            ans = laya_res.get("answers", laya_res.get("recommended_defaults", {}))
            arch = ans.get("camera_switch_archetype", {}).get("choice", "reaction_cutaway_insert")
            if arch in ("wide_group_interaction", "reaction_cutaway_insert"):
                return {
                    "role": "WIDE",
                    "camera": wide_cam,
                    "scale": 100.0,
                    "beat": "MONOLOGUE_BREATHER_WIDE",
                    "reason": f"Laya Decision ({arch}): Visual breather Wide shot after {consecutive_same_angle_sec:.1f}s continuous Close-Up",
                    "laya_invoked": bool(laya_res.get("laya_called", False)),
                }
        return {
            "role": target_role,
            "camera": target_cam,
            "scale": 108.0,
            "beat": f"SPEAKER_{speaker}_PUNCH_IN",
            "reason": f"Subtle 108% punch-in on {speaker} Close-Up to maintain momentum across long monologue",
            "laya_invoked": False,
        }

    # Rule 4: Standard Active Speaker Close-Up
    # If cutting from the exact same camera after a silence removal, alternate 100% / 108% scale to hide jump cut
    scale = 108.0 if (target_role == prev_angle and dur >= 3.0) else 100.0
    return {
        "role": target_role,
        "camera": target_cam,
        "scale": scale,
        "beat": f"ACTIVE_SPEAKER_{speaker}",
        "reason": f"{speaker} is speaking solo ({dur:.1f}s) -> Close-Up on {target_cam}" + (" (108% punch-in)" if scale > 100 else ""),
        "laya_invoked": False,
    }


def install_laya_package() -> Dict[str, Any]:
    """Install NandhaKishorM/laya via pip (`pip install laya` with GitHub fallback)."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "laya"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if proc.returncode != 0:
            proc = subprocess.run(
                [sys.executable, "-m", "pip", "install", f"git+{LAYA_REPO_URL}.git"],
                capture_output=True,
                text=True,
                timeout=300,
            )
        return {
            "status": "installed" if proc.returncode == 0 else "failed",
            "returncode": proc.returncode,
            "stdout": proc.stdout[-600:],
            "stderr": proc.stderr[-600:],
        }
    except Exception as exc:
        return {"status": "failed", "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"Laya Decision Gate for {APP_LABEL} ({LAYA_REPO_URL}) — Calls Laya ONLY when necessary."
    )
    parser.add_argument("--state", type=str, default="", help="Natural-language brief or podcast segment state")
    parser.add_argument("--questions-json", type=str, default="", help="Optional path or inline JSON of Laya questions")
    parser.add_argument("--force-laya", action="store_true", help="Force calling Laya even for short/basic states")
    parser.add_argument("--min-confidence", type=float, default=0.55, help="Minimum confidence threshold (default: 0.55)")
    parser.add_argument("--install", action="store_true", help="Install the `laya` package (https://github.com/NandhaKishorM/laya)")
    args = parser.parse_args()

    if args.install:
        res = install_laya_package()
        print(json.dumps(res, indent=2))
        return 0 if res.get("status") == "installed" else 1

    custom_questions = None
    if args.questions_json:
        q_path = Path(args.questions_json)
        if q_path.exists():
            custom_questions = json.loads(q_path.read_text(encoding="utf-8"))
        else:
            custom_questions = json.loads(args.questions_json)

    result = evaluate_decision(
        state_text=args.state,
        questions=custom_questions,
        force_laya=args.force_laya,
        min_confidence=args.min_confidence,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
