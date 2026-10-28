#!/usr/bin/env python3
"""Validate a Maya/Three.js shared scene specification without external packages."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


UNITS = {"mm", "cm", "m", "in", "ft"}
PART_TYPES = {"box", "cylinder", "sphere", "tube", "extrude"}
MAYA_SAFE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _vector(value: Any, length: int) -> bool:
    return isinstance(value, list) and len(value) == length and all(
        isinstance(item, (int, float)) and not isinstance(item, bool) for item in value
    )


def _positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def validate(spec: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(spec, dict):
        return ["Scene specification must be a JSON object."], warnings
    if spec.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1.")
    if spec.get("units") not in UNITS:
        errors.append("units must be one of mm, cm, m, in, or ft.")
    parts = spec.get("parts")
    if not isinstance(parts, list) or not parts:
        errors.append("parts must contain at least one part.")
        parts = []

    materials = spec.get("materials") if isinstance(spec.get("materials"), dict) else {}
    anchors = spec.get("anchors") if isinstance(spec.get("anchors"), dict) else {}
    for name, point in anchors.items():
        if not _vector(point, 3):
            errors.append(f"Anchor {name} must be a three-number array.")

    names: set[str] = set()
    for index, part in enumerate(parts):
        prefix = f"parts[{index}]"
        if not isinstance(part, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        name = part.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix}.name is required.")
        elif not MAYA_SAFE_NAME.fullmatch(name):
            errors.append(f"{prefix}.name must be a Maya-safe identifier using letters, numbers, and underscores.")
        elif name in names:
            errors.append(f"Part name {name} is duplicated.")
        else:
            names.add(name)
        part_type = part.get("type")
        if part_type not in PART_TYPES:
            errors.append(f"{prefix}.type must be box, cylinder, sphere, tube, or extrude.")
        if "position" in part and not _vector(part["position"], 3):
            errors.append(f"{prefix}.position must be a three-number array.")
        if "rotation" in part and not _vector(part["rotation"], 3):
            errors.append(f"{prefix}.rotation must be a three-number array in degrees.")
        if "scale" in part and (not _vector(part["scale"], 3) or any(value <= 0 for value in part["scale"])):
            errors.append(f"{prefix}.scale must contain three positive numbers.")
        if part.get("material") and part["material"] not in materials:
            errors.append(f"{prefix}.material references undefined material {part['material']}.")

        if part_type == "box" and (not _vector(part.get("size"), 3) or any(value <= 0 for value in part["size"])):
            errors.append(f"{prefix}.size must contain three positive numbers.")
        elif part_type == "cylinder" and (not _positive(part.get("radius")) or not _positive(part.get("height"))):
            errors.append(f"{prefix} cylinder requires positive radius and height.")
        elif part_type == "sphere" and not _positive(part.get("radius")):
            errors.append(f"{prefix} sphere requires a positive radius.")
        elif part_type == "tube":
            path = part.get("path")
            if not isinstance(path, list) or len(path) < 2 or not all(_vector(point, 3) for point in path):
                errors.append(f"{prefix}.path must contain at least two three-number points.")
            if not _positive(part.get("radius")):
                errors.append(f"{prefix} tube requires a positive radius.")
            for key in ("startAnchor", "endAnchor"):
                if part.get(key) and part[key] not in anchors:
                    errors.append(f"{prefix}.{key} references undefined anchor {part[key]}.")
            if not part.get("startAnchor") or not part.get("endAnchor"):
                warnings.append(f"{name or prefix} has no complete endpoint-anchor constraint.")
        elif part_type == "extrude":
            profile = part.get("profile")
            if not isinstance(profile, list) or len(profile) < 3 or not all(_vector(point, 2) for point in profile):
                errors.append(f"{prefix}.profile must contain at least three two-number points.")
            if not _positive(part.get("depth")):
                errors.append(f"{prefix} extrude requires a positive depth.")

    connections = spec.get("connections", [])
    if not isinstance(connections, list):
        errors.append("connections must be an array.")
        connections = []
    for connection in connections:
        if not isinstance(connection, dict):
            errors.append("Each connection must be an object.")
            continue
        if connection.get("from") not in names:
            errors.append(f"Connection references unknown from part {connection.get('from')}.")
        if connection.get("to") not in names:
            errors.append(f"Connection references unknown to part {connection.get('to')}.")
        max_gap = connection.get("maxGap")
        if not isinstance(max_gap, (int, float)) or isinstance(max_gap, bool) or max_gap < 0:
            errors.append(f"Connection {connection.get('from')} → {connection.get('to')} requires a non-negative maxGap.")

    symmetry_pairs = spec.get("symmetryPairs", [])
    if not isinstance(symmetry_pairs, list):
        errors.append("symmetryPairs must be an array.")
        symmetry_pairs = []
    for pair in symmetry_pairs:
        if not isinstance(pair, dict):
            errors.append("Each symmetry pair must be an object.")
            continue
        if pair.get("left") not in names:
            errors.append(f"Symmetry pair references unknown left part {pair.get('left')}.")
        if pair.get("right") not in names:
            errors.append(f"Symmetry pair references unknown right part {pair.get('right')}.")
        if pair.get("axis") not in {"X", "Y", "Z"}:
            errors.append(f"Symmetry pair {pair.get('left')} / {pair.get('right')} requires axis X, Y, or Z.")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_spec", type=Path)
    args = parser.parse_args()
    try:
        spec = json.loads(args.scene_spec.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)], "warnings": []}, indent=2))
        return 2
    errors, warnings = validate(spec)
    print(json.dumps({"valid": not errors, "errors": errors, "warnings": warnings}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
