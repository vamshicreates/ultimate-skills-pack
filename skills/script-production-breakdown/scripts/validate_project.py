#!/usr/bin/env python3
"""Validate file and scene bookkeeping for a production-breakdown project."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


SCENE_ID = re.compile(r"^SC-\d{3,}$")


def load_json(path: Path, errors: list[str]) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required file: {path.name}")
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {path.name}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path.name} must contain a JSON object")
        return {}
    return data


def scene_records(data: dict[str, object], errors: list[str]) -> list[dict[str, object]]:
    scenes = data.get("scenes")
    if not isinstance(scenes, list):
        errors.append("production-data.json must contain a scenes array")
        return []
    valid: list[dict[str, object]] = []
    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            errors.append(f"scenes[{index}] must be an object")
            continue
        valid.append(scene)
    return valid


def validate_scene_files(root: Path, scenes: list[dict[str, object]], errors: list[str]) -> None:
    seen: set[str] = set()
    for index, scene in enumerate(scenes):
        raw_id = scene.get("scene_id")
        if not isinstance(raw_id, str) or not SCENE_ID.fullmatch(raw_id):
            errors.append(f"scenes[{index}] has invalid scene_id: {raw_id!r}")
            continue
        if raw_id in seen:
            errors.append(f"duplicate scene_id: {raw_id}")
            continue
        seen.add(raw_id)

        state = scene.get("completion_state", "indexed")
        if state not in {"indexed", "breakdown_complete", "storyboard_complete", "reviewed"}:
            errors.append(f"{raw_id} has invalid completion_state: {state!r}")

        if state in {"storyboard_complete", "reviewed"}:
            scene_dir = root / "scenes" / raw_id
            storyboard = scene_dir / "storyboard-3x3.png"
            breakdown = scene_dir / "breakdown.md"
            if not storyboard.is_file() or storyboard.stat().st_size == 0:
                errors.append(f"{raw_id} is missing a non-empty storyboard-3x3.png")
            if not breakdown.is_file() or breakdown.stat().st_size == 0:
                errors.append(f"{raw_id} is missing a non-empty breakdown.md")


def validate_counts(data: dict[str, object], scenes: list[dict[str, object]], errors: list[str]) -> None:
    declared = data.get("indexed_scene_count")
    if not isinstance(declared, int):
        errors.append("production-data.json must contain integer indexed_scene_count")
    elif declared != len(scenes):
        errors.append(f"indexed_scene_count is {declared}, but scenes contains {len(scenes)} records")


def validate_summary_csv(root: Path, scene_ids: set[str], errors: list[str]) -> None:
    path = root / "master-scene-summary.csv"
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    except FileNotFoundError:
        errors.append(f"missing required file: {path.name}")
        return
    except OSError as exc:
        errors.append(f"cannot read {path.name}: {exc}")
        return

    if not rows:
        errors.append(f"{path.name} contains no scene rows")
        return
    csv_ids = {row.get("scene_id", "") for row in rows}
    missing = scene_ids - csv_ids
    extra = csv_ids - scene_ids
    if missing:
        errors.append(f"{path.name} is missing scene IDs: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"{path.name} contains unknown scene IDs: {', '.join(sorted(extra))}")


def validate_master_order(root: Path, completed_ids: list[str], errors: list[str]) -> None:
    path = root / "master-production-breakdown.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing required file: {path.name}")
        return
    except OSError as exc:
        errors.append(f"cannot read {path.name}: {exc}")
        return

    for scene_id in completed_ids:
        start = text.find(scene_id)
        if start < 0:
            errors.append(f"{path.name} does not contain {scene_id}")
            continue
        next_scene = text.find("\n# SC-", start + len(scene_id))
        section = text[start : next_scene if next_scene >= 0 else None]
        image_pos = section.find("storyboard-3x3.png")
        breakdown_positions = [
            pos
            for label in ("## Scene summary", "## Production breakdown")
            if (pos := section.find(label)) >= 0
        ]
        breakdown_pos = min(breakdown_positions) if breakdown_positions else -1
        if image_pos < 0:
            errors.append(f"{scene_id} has no storyboard image link in {path.name}")
        elif breakdown_pos >= 0 and image_pos > breakdown_pos:
            errors.append(f"{scene_id} storyboard appears after its breakdown in {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="Path to the production-breakdown folder")
    args = parser.parse_args()
    root = Path(args.project).expanduser().resolve()
    errors: list[str] = []

    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    manifest = load_json(root / "script-manifest.json", errors)
    if manifest and not manifest.get("source_file"):
        errors.append("script-manifest.json must contain source_file")

    data = load_json(root / "production-data.json", errors)
    scenes = scene_records(data, errors) if data else []
    validate_counts(data, scenes, errors)
    validate_scene_files(root, scenes, errors)

    scene_ids = {
        scene["scene_id"]
        for scene in scenes
        if isinstance(scene.get("scene_id"), str) and SCENE_ID.fullmatch(scene["scene_id"])
    }
    completed_ids = [
        scene["scene_id"]
        for scene in scenes
        if scene.get("completion_state") in {"storyboard_complete", "reviewed"}
        and isinstance(scene.get("scene_id"), str)
    ]
    validate_summary_csv(root, scene_ids, errors)
    validate_master_order(root, completed_ids, errors)

    for required in ("continuity-report.md",):
        path = root / required
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty required file: {required}")

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Validation passed: {len(scenes)} indexed scenes, "
        f"{len(completed_ids)} completed storyboards"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
