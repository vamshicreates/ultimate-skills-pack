#!/usr/bin/env python3
"""Validate job batches and retain seen-job and feedback state.

The script stores only public job metadata and user preference signals. It does
not store candidate contact details or submit applications.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


DEFAULT_STATE_DIR = Path(".job-hunter") / "sagar-design-job-hunter"
REQUIRED_FIELDS = {
    "company",
    "role",
    "location",
    "salary",
    "why_fit",
    "match_score",
    "apply_url",
    "source_url",
    "verified_at",
}
TRACKING_KEYS = {
    "fbclid",
    "gclid",
    "ref",
    "referrer",
    "source",
    "trackingid",
    "trk",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_url(raw: str) -> str:
    value = raw.strip()
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Not an absolute HTTP(S) URL: {raw!r}")
    query = [
        (key, val)
        for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_KEYS and not key.lower().startswith("utm_")
    ]
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, urlencode(query), ""))


def load_state(path: Path) -> dict:
    if not path.exists():
        return {
            "version": 1,
            "profile_url": "https://www.behance.net/sagardabherao",
            "target_locations": ["Hyderabad", "Secunderabad"],
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "batches": [],
            "seen_urls": [],
            "preference_signals": {"positive": [], "negative": []},
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ValueError("Unsupported state version")
    return data


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_iso()
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_indices(value: Optional[str], job_count: int) -> List[int]:
    if not value:
        return []
    if value.strip().lower() == "all":
        return list(range(1, job_count + 1))
    result: List[int] = []
    for part in value.split(","):
        try:
            index = int(part.strip())
        except ValueError as exc:
            raise ValueError(f"Invalid job index: {part!r}") from exc
        if index < 1 or index > job_count:
            raise ValueError(f"Job index {index} is outside 1..{job_count}")
        if index not in result:
            result.append(index)
    return result


def validate_job(job: object, position: int) -> dict:
    if not isinstance(job, dict):
        raise ValueError(f"Job #{position} must be an object")
    missing = sorted(REQUIRED_FIELDS - set(job))
    if missing:
        raise ValueError(f"Job #{position} is missing: {', '.join(missing)}")
    for key in REQUIRED_FIELDS - {"match_score"}:
        if not isinstance(job[key], str) or not job[key].strip():
            raise ValueError(f"Job #{position} field {key!r} must be a non-empty string")
    score = job["match_score"]
    if isinstance(score, str) and score.endswith("%"):
        score = score[:-1]
    try:
        numeric_score = int(score)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Job #{position} match_score must be an integer from 0 to 100") from exc
    if numeric_score < 0 or numeric_score > 100:
        raise ValueError(f"Job #{position} match_score must be from 0 to 100")
    normalized = dict(job)
    normalized["match_score"] = numeric_score
    normalized["apply_url"] = canonical_url(job["apply_url"])
    normalized["source_url"] = canonical_url(job["source_url"])
    for key in ("cautions", "evidence"):
        if key in normalized and not isinstance(normalized[key], list):
            raise ValueError(f"Job #{position} optional field {key!r} must be an array")
    return normalized


def read_batch(path: Path, allow_partial: bool) -> Tuple[Optional[str], List[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    batch_id = None
    if isinstance(payload, dict):
        batch_id = payload.get("batch_id")
        jobs = payload.get("jobs")
    else:
        jobs = payload
    if not isinstance(jobs, list):
        raise ValueError("Batch JSON must be a job array or an object containing a jobs array")
    if len(jobs) > 5:
        raise ValueError("A batch may contain no more than five jobs")
    if len(jobs) != 5 and not allow_partial:
        raise ValueError("A normal batch must contain exactly five jobs; use --allow-partial for a verified shortfall")
    if not jobs:
        raise ValueError("A batch must contain at least one job")
    validated = [validate_job(job, index) for index, job in enumerate(jobs, start=1)]
    apply_urls = [job["apply_url"] for job in validated]
    if len(set(apply_urls)) != len(apply_urls):
        raise ValueError("The batch contains duplicate application URLs")
    return batch_id, validated


def command_record(args: argparse.Namespace, state_path: Path) -> None:
    state = load_state(state_path)
    requested_id, jobs = read_batch(Path(args.batch), args.allow_partial)
    seen = set(state.get("seen_urls", []))
    repeated = [job["apply_url"] for job in jobs if job["apply_url"] in seen]
    if repeated:
        raise ValueError("Already-seen application URL(s): " + ", ".join(repeated))
    digest_input = "\n".join(job["apply_url"] for job in jobs).encode("utf-8")
    batch_id = requested_id or f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{hashlib.sha256(digest_input).hexdigest()[:8]}"
    if any(batch.get("batch_id") == batch_id for batch in state["batches"]):
        raise ValueError(f"Batch id already exists: {batch_id}")
    batch = {
        "batch_id": batch_id,
        "created_at": now_iso(),
        "jobs": jobs,
        "feedback": {"approved": [], "rejected": [], "reason": None, "updated_at": None},
    }
    state["batches"].append(batch)
    state["seen_urls"] = sorted(seen | {job["apply_url"] for job in jobs})
    save_state(state_path, state)
    print(json.dumps({"status": "RECORDED", "batch_id": batch_id, "job_count": len(jobs)}, indent=2))


def command_feedback(args: argparse.Namespace, state_path: Path) -> None:
    state = load_state(state_path)
    batch = next((item for item in state["batches"] if item.get("batch_id") == args.batch_id), None)
    if batch is None:
        raise ValueError(f"Unknown batch id: {args.batch_id}")
    count = len(batch["jobs"])
    approved = parse_indices(args.approved, count)
    rejected = parse_indices(args.rejected, count)
    overlap = sorted(set(approved) & set(rejected))
    if overlap:
        raise ValueError("The same job cannot be approved and rejected: " + ", ".join(map(str, overlap)))
    if not approved and not rejected:
        raise ValueError("Provide --approved, --rejected, or both")
    feedback = batch.setdefault("feedback", {})
    approved_set = (set(feedback.get("approved", [])) - set(rejected)) | set(approved)
    rejected_set = (set(feedback.get("rejected", [])) - set(approved)) | set(rejected)
    feedback["approved"] = sorted(approved_set)
    feedback["rejected"] = sorted(rejected_set)
    feedback["updated_at"] = now_iso()
    if args.reason:
        feedback["reason"] = args.reason.strip()
        signal_key = "negative" if rejected else "positive"
        signals = state.setdefault("preference_signals", {}).setdefault(signal_key, [])
        if args.reason.strip() not in signals:
            signals.append(args.reason.strip())
    save_state(state_path, state)
    print(json.dumps({"status": "UPDATED", "batch_id": args.batch_id, "feedback": feedback}, indent=2))


def command_show(state_path: Path) -> None:
    state = load_state(state_path)
    summary = {
        "state_file": str(state_path.resolve()),
        "profile_url": state.get("profile_url"),
        "target_locations": state.get("target_locations", []),
        "batch_count": len(state.get("batches", [])),
        "seen_urls": state.get("seen_urls", []),
        "preference_signals": state.get("preference_signals", {}),
        "latest_batch": state.get("batches", [])[-1] if state.get("batches") else None,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR), help="Directory containing state.json")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record-batch", help="Validate and record a new job batch")
    record.add_argument("--batch", required=True, help="Path to batch JSON")
    record.add_argument("--allow-partial", action="store_true", help="Permit a verified batch with fewer than five jobs")

    feedback = sub.add_parser("feedback", help="Record approvals and rejections")
    feedback.add_argument("--batch-id", required=True)
    feedback.add_argument("--approved", help="Comma-separated indices or 'all'")
    feedback.add_argument("--rejected", help="Comma-separated indices or 'all'")
    feedback.add_argument("--reason", help="User's wording for the preference signal")

    sub.add_parser("show", help="Show compact state and the latest batch")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    state_path = Path(args.state_dir) / "state.json"
    try:
        if args.command == "record-batch":
            command_record(args, state_path)
        elif args.command == "feedback":
            command_feedback(args, state_path)
        else:
            command_show(state_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
