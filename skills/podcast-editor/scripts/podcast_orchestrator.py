#!/usr/bin/env python3
"""
End-to-End Cross-Platform (Windows & macOS) Orchestrator for `podcast-editor`
(`scripts/podcast_orchestrator.py`).

Pipeline Stages:
0. NLE Selection Gate: Requires explicit `--nle premiere` (Primary Default) or `--nle davinci`
   confirmed by the user before launching live NLE execution.
1. Ingest & Waveform Sync (`podcast_ingest_sync.py`) -> `edit/sync_map.json`
2. Hybrid Voice Diarization (`podcast_voice_diarize.py`) -> `edit/takes_packed.md` & `edit/diarized_segments.json`
3. Zero-Token Visual Shot & Lip-Motion Classifier (`podcast_vision_classifier.py`) -> `edit/camera_roles.json` & `edit/verify/camera_assignment_sheet.png`
4. Laya Multicam EDL Director (`podcast_edl_director.py`) -> `edit/edl.json`, `edit/timeline_spec.json`, `edit/podcast_master.xml`, `edit/podcast_master.fcpxml`, `edit/master.srt`
5. Live Foreground NLE Execution (`live_premiere_podcast_builder.py` OR `live_davinci_podcast_builder.py`) -> Live visible timeline construction + `edit/final_podcast.mp4` + Self-Eval.
"""

import argparse
import json
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from live_davinci_podcast_builder import execute_live_podcast_in_davinci, get_resolve_paths  # noqa: E402
from live_premiere_podcast_builder import execute_live_podcast_in_premiere, find_premiere_executable  # noqa: E402
from podcast_edl_director import build_podcast_multicam_edl  # noqa: E402
from podcast_ingest_sync import ingest_and_sync_podcast  # noqa: E402
from podcast_vision_classifier import classify_cameras_and_speakers  # noqa: E402
from podcast_voice_diarize import run_voice_diarization  # noqa: E402


def check_environment_status() -> Dict[str, Any]:
    ppro = find_premiere_executable()
    resolve_info = get_resolve_paths()
    return {
        "os": platform.system(),
        "premiere_pro": {
            "installed": ppro is not None,
            "executable": ppro,
            "priority": "primary",
        },
        "davinci_resolve": {
            "installed": resolve_info.get("installed", False),
            "app_path": resolve_info.get("app_path"),
            "priority": "secondary",
        },
    }


def run_podcast_pipeline(
    project_dir: Path,
    nle: Optional[str] = None,
    mode: str = "execute",
    cam1: Optional[str] = None,
    cam2: Optional[str] = None,
    cam3: Optional[str] = None,
    audio_paths: Optional[List[str]] = None,
    num_speakers: int = 2,
    brief: str = "",
    burn_subtitles: bool = False,
) -> Dict[str, Any]:
    project_dir = project_dir.resolve()
    edit_dir = project_dir / "edit"
    edit_dir.mkdir(parents=True, exist_ok=True)

    # Hard Rule: Enforce User NLE Selection Gate before executing NLE timeline build
    if mode == "execute" and not nle:
        return {
            "status": "AWAITING_USER_NLE_CHOICE",
            "message": (
                "STOP: Before proceeding with live timeline editing, ask the user which software "
                "they prefer to edit with: Adobe Premiere Pro (Recommended Primary) or DaVinci Resolve."
            ),
            "available_nles": check_environment_status(),
        }

    # Phase 1: Ingest Camera 1, Camera 2, Camera 3 + Audio & Waveform Sync
    sync_res = ingest_and_sync_podcast(
        project_dir=project_dir,
        cam1=cam1,
        cam2=cam2,
        cam3=cam3,
        audio_paths=audio_paths,
        edit_dir=edit_dir,
    )
    if sync_res.get("status") != "success":
        return {"status": "error", "stage": "ingest_sync", "details": sync_res}
    sync_map_path = edit_dir / "sync_map.json"

    # Phase 2: Hybrid Auto Voice Diarization -> takes_packed.md & diarized_segments.json
    diar_res = run_voice_diarization(
        sync_map_path=sync_map_path,
        num_speakers=num_speakers,
    )
    if diar_res.get("status") != "success":
        return {"status": "error", "stage": "voice_diarization", "details": diar_res}
    diarized_path = edit_dir / "diarized_segments.json"

    # Phase 3: Visual Shot & Active-Speaker Lip-Motion Classification -> camera_roles.json
    vision_res = classify_cameras_and_speakers(
        sync_map_path=sync_map_path,
        diarized_path=diarized_path,
    )
    if vision_res.get("status") != "success":
        return {"status": "error", "stage": "vision_classifier", "details": vision_res}
    camera_roles_path = edit_dir / "camera_roles.json"

    # Phase 4: Laya Decision Model + Multicam EDL Director -> edl.json, timeline_spec.json, XML, FCPXML, SRT
    edl_res = build_podcast_multicam_edl(
        sync_map_path=sync_map_path,
        diarized_path=diarized_path,
        camera_roles_path=camera_roles_path,
        brief_text=brief,
    )
    if edl_res.get("status") != "success":
        return {"status": "error", "stage": "edl_director", "details": edl_res}

    if mode == "preflight":
        return {
            "status": "PREFLIGHT_READY",
            "project_dir": str(project_dir),
            "edit_dir": str(edit_dir),
            "camera_roles": vision_res.get("roles"),
            "verification_sheet_png": vision_res.get("verification_sheet_png"),
            "takes_packed_md": diar_res.get("takes_packed_md"),
            "edl_summary": edl_res,
            "next_step": "Confirm NLE choice (Premiere Pro or DaVinci Resolve) and strategy with the user, then run with `--mode execute --nle <premiere|davinci>`.",
        }

    # Phase 5: Live Foreground NLE Execution (Visible on screen!)
    nle_norm = nle.strip().lower()
    spec_path = edit_dir / "timeline_spec.json"
    edl_path = edit_dir / "edl.json"

    if nle_norm in ("premiere", "premiere-pro", "premiere_pro", "ppro", "adobe"):
        nle_res = execute_live_podcast_in_premiere(
            timeline_spec_path=spec_path,
            edl_path=edl_path,
            burn_subtitles=burn_subtitles,
        )
    elif nle_norm in ("davinci", "resolve", "davinci-resolve", "davinci_resolve"):
        nle_res = execute_live_podcast_in_davinci(
            timeline_spec_path=spec_path,
            edl_path=edl_path,
            burn_subtitles=burn_subtitles,
        )
    else:
        return {"status": "error", "message": f"Unsupported --nle '{nle}'. Choose 'premiere' or 'davinci'."}

    # Append session summary to `edit/project.md` (per video-use persistence rule)
    proj_md = edit_dir / "project.md"
    summary_block = (
        f"## Podcast Edit Session ({nle_res.get('nle')})\n"
        f"- **OS**: {platform.system()}\n"
        f"- **Camera Roles**: `{json.dumps(vision_res.get('roles', {}))}`\n"
        f"- **Total Switched Cuts**: {edl_res.get('total_cuts')}\n"
        f"- **Final Duration**: {edl_res.get('total_duration_sec')}s\n"
        f"- **Final Master MP4**: `{nle_res.get('final_render', {}).get('final_podcast_mp4')}`\n"
        f"- **Premiere/Resolve XML**: `{edl_res.get('xmeml_v4_xml')}`\n"
        f"- **Resolve/FCP FCPXML**: `{edl_res.get('fcpxml_v110')}`\n"
        f"- **Master Captions**: `{edl_res.get('master_srt')}`\n\n"
    )
    with open(proj_md, "a", encoding="utf-8") as f:
        f.write(summary_block)

    return {
        "status": "success",
        "selected_nle": nle_res.get("nle"),
        "project_dir": str(project_dir),
        "edit_dir": str(edit_dir),
        "camera_roles": vision_res.get("roles"),
        "verification_sheet_png": vision_res.get("verification_sheet_png"),
        "diarization": {
            "asr_backend": diar_res.get("asr_backend"),
            "diarization_mode": diar_res.get("diarization_mode"),
            "takes_packed_md": diar_res.get("takes_packed_md"),
        },
        "edl_summary": edl_res,
        "live_nle_execution": nle_res,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-Platform Multi-Cam Podcast Editor Orchestrator")
    parser.add_argument("--project-dir", type=Path, default=Path("."), help="Folder containing Camera 1, Camera 2, Camera 3")
    parser.add_argument("--mode", choices=["setup", "status", "preflight", "execute"], default="execute", help="Pipeline execution mode")
    parser.add_argument("--nle", choices=["premiere", "davinci"], default=None, help="User-selected NLE ('premiere' or 'davinci')")
    parser.add_argument("--cam1", type=str, default=None, help="Optional explicit path to Camera 1")
    parser.add_argument("--cam2", type=str, default=None, help="Optional explicit path to Camera 2")
    parser.add_argument("--cam3", type=str, default=None, help="Optional explicit path to Camera 3")
    parser.add_argument("--audio", nargs="*", default=None, help="Optional explicit audio file(s) or folder")
    parser.add_argument("--num-speakers", type=int, default=2, help="Number of podcast speakers (default: 2)")
    parser.add_argument("--brief", type=str, default="", help="Optional editorial brief for Laya Decision Router")
    parser.add_argument("--burn-subtitles", action="store_true", help="Burn master.srt captions into final_podcast.mp4")
    args = parser.parse_args()

    if args.mode == "setup":
        from setup_podcast_editor import run_setup

        print(json.dumps(run_setup(install_laya=False), indent=2))
        return 0

    if args.mode == "status":
        from setup_podcast_editor import run_setup

        print(json.dumps(run_setup(install_laya=False), indent=2))
        return 0

    res = run_podcast_pipeline(
        project_dir=args.project_dir,
        nle=args.nle,
        mode=args.mode,
        cam1=args.cam1,
        cam2=args.cam2,
        cam3=args.cam3,
        audio_paths=args.audio,
        num_speakers=args.num_speakers,
        brief=args.brief,
        burn_subtitles=args.burn_subtitles,
    )
    print(json.dumps(res, indent=2))
    return 0 if res.get("status") in ("success", "PREFLIGHT_READY", "AWAITING_USER_NLE_CHOICE") else 1


if __name__ == "__main__":
    sys.exit(main())
