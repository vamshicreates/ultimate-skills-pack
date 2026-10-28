#!/usr/bin/env python3
"""Validate editorial scorecards and calculate comparable screenplay rankings."""

import argparse
import csv
import io
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


RUBRIC_ID = "script-doctor-v1"
WEIGHTS = {
    "character": 15, "plot": 15, "emotion": 20, "structure": 15,
    "dialogue": 10, "theme": 10, "cinematic": 10, "specificity": 5,
}
FORMATS = ("unspecified", "micro_drama", "short_film", "feature", "web_series", "other")
UNITS = ("unspecified", "standalone", "episode", "pilot", "season", "series", "excerpt", "treatment")
RUNTIME_BASES = ("unknown", "user_stated", "timed_read", "estimated")


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError(f"{label} must be finite")
    return result


def validate_weights(value):
    if not isinstance(value, dict) or set(value) != set(WEIGHTS):
        raise ValueError("weights must contain exactly the eight rubric categories")
    weights = {key: number(value[key], f"weight {key}") for key in WEIGHTS}
    if any(weight < 0 for weight in weights.values()) or sum(weights.values()) != 100:
        raise ValueError("weights must be nonnegative and sum to 100")
    return weights


def evaluation_context(entry):
    """Keep runtime descriptive; grouping is editorial, never a score multiplier."""
    script_id = entry["id"]
    form = entry.get("format", "unspecified")
    unit = entry.get("evaluation_unit", "unspecified")
    basis = entry.get("runtime_basis", "unknown")
    if form not in FORMATS:
        raise ValueError(f"{script_id}: unsupported format; use one of {FORMATS}")
    if unit not in UNITS:
        raise ValueError(f"{script_id}: unsupported evaluation_unit; use one of {UNITS}")
    if basis not in RUNTIME_BASES:
        raise ValueError(f"{script_id}: unsupported runtime_basis; use one of {RUNTIME_BASES}")
    runtime = entry.get("runtime_minutes")
    if runtime is not None:
        if number(runtime, f"{script_id}.runtime_minutes") <= 0:
            raise ValueError(f"{script_id}: runtime_minutes must be positive or null")
        if basis == "unknown":
            raise ValueError(f"{script_id}: a numeric runtime needs its runtime_basis")
    elif basis != "unknown":
        raise ValueError(f"{script_id}: runtime_basis requires runtime_minutes; describe ranges in the report")
    for field in ("series_id", "episode_id"):
        if field in entry:
            require_text(entry[field], f"{script_id}.{field}")
    default_group = "all" if (form, unit) == ("unspecified", "unspecified") else f"{form}/{unit}"
    group = require_text(entry.get("comparison_group", default_group), f"{script_id}.comparison_group")
    return {"format": form, "evaluation_unit": unit, "runtime_minutes": runtime,
            "runtime_basis": basis, "comparison_group": group}


def evaluate(data):
    """Return totals/ranks; incomplete or low-confidence readings remain unranked."""
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    rubric_id = require_text(data.get("rubric_id"), "rubric_id")
    weights = validate_weights(data.get("weights"))
    if rubric_id == RUBRIC_ID and weights != WEIGHTS:
        raise ValueError("custom weights require a distinct rubric_id")
    if weights == WEIGHTS and rubric_id != RUBRIC_ID:
        raise ValueError(f"default weights must use rubric_id {RUBRIC_ID}")
    entries = data.get("scripts")
    if not isinstance(entries, list) or not entries:
        raise ValueError("scripts must be a nonempty list")

    rows, seen = [], set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"scripts[{index}] must be an object")
        for key in ("id", "title", "source", "draft", "language", "genre", "rubric_id"):
            require_text(entry.get(key), f"scripts[{index}].{key}")
        context = evaluation_context(entry)
        script_id = entry["id"]
        if script_id in seen:
            raise ValueError(f"duplicate script id: {script_id}")
        seen.add(script_id)
        if entry["rubric_id"] != rubric_id or "weights" in entry:
            raise ValueError(f"{script_id}: every row must use the shared rubric/weights")
        if entry.get("role") not in ("candidate", "reference"):
            raise ValueError(f"{script_id}: role must be candidate or reference")
        if entry.get("read_status") not in ("complete", "partial", "unreadable"):
            raise ValueError(f"{script_id}: read_status must be complete, partial, or unreadable")
        if entry.get("confidence") not in ("high", "medium", "low"):
            raise ValueError(f"{script_id}: confidence must be high, medium, or low")
        limitations = entry.get("limitations")
        if not isinstance(limitations, list) or any(
            not isinstance(item, str) or not item.strip() for item in limitations
        ):
            raise ValueError(f"{script_id}: limitations must be a list of nonempty strings")
        scores = entry.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(WEIGHTS):
            raise ValueError(f"{script_id}: scores must contain all eight category keys")
        values = {}
        for key in WEIGHTS:
            if scores[key] is None:
                values[key] = None
                continue
            value = number(scores[key], f"{script_id}.{key}")
            if value < 0 or value > 10 or value * 2 != (value * 2).to_integral_value():
                raise ValueError(f"{script_id}.{key}: score must be 0–10 in half-point steps")
            values[key] = value

        reasons = []
        if context["evaluation_unit"] in ("excerpt", "treatment"):
            reasons.append("excerpt/treatment scope is not a complete dramatic script")
        if entry["read_status"] != "complete":
            reasons.append(f"reading is {entry['read_status']}")
        if entry["confidence"] == "low":
            reasons.append("material assessment uncertainty")
        missing = [key for key in WEIGHTS if weights[key] > 0 and values[key] is None]
        if missing:
            reasons.append("unassessed categories: " + ", ".join(missing))
        if reasons and not limitations:
            raise ValueError(f"{script_id}: explain incomplete/uncertain assessment in limitations")

        total = None
        if not reasons:
            weighted = sum(
                values[key] * weights[key] / 10 for key in WEIGHTS if weights[key] > 0
            )
            total = int(weighted.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        rank_reasons = list(reasons)
        if entry["role"] == "reference":
            rank_reasons.append("reference excluded from candidate ranking")
        rows.append({
            **entry, **context, "total": total, "rank": None, "close_to": [],
            "unranked_reasons": rank_reasons,
        })

    ranked, groups = [], []
    for group_name in sorted({row["comparison_group"] for row in rows}):
        members = [row for row in rows if row["comparison_group"] == group_name]
        eligible = sorted((row for row in members if not row["unranked_reasons"]),
                          key=lambda row: (-row["total"], row["id"]))
        previous_score, previous_rank = None, None
        for position, row in enumerate(eligible, 1):
            if row["total"] != previous_score:
                previous_rank = position
            row["rank"] = previous_rank
            previous_score = row["total"]
            row["close_to"] = [
                other["id"] for other in eligible
                if other["id"] != row["id"] and abs(other["total"] - row["total"]) <= 2
            ]
        ranked.extend(eligible)
        groups.append({"name": group_name, "ranked_count": len(eligible),
                       "unranked_count": len(members) - len(eligible)})
    unranked = [row for row in rows if row["rank"] is None]
    return {
        "rubric_id": rubric_id,
        "weights": data["weights"],
        "rounding": "Nearest integer; halves round up; round once after weighting.",
        "close_call_threshold": 2,
        "ranking_scope": "within comparison_group",
        "groups": groups,
        "note": "Editorial judgments, not measured audience responses or commercial predictions.",
        "ranked_count": len(ranked),
        "unranked_count": len(unranked),
        "scripts": ranked + unranked,
    }


def csv_cell(value):
    if value is None:
        return ""
    if isinstance(value, list):
        value = " | ".join(value)
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def render_csv(result):
    columns = [
        "comparison_group", "rank", "id", "title", "draft", "source", "role", "language", "genre",
        "format", "evaluation_unit", "runtime_minutes", "runtime_basis", "series_id", "episode_id",
        "total", "confidence", "read_status", "rubric_id", *WEIGHTS,
        "close_to", "unranked_reasons", "limitations",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in result["scripts"]:
        flat = {**row, **row["scores"]}
        writer.writerow({key: csv_cell(flat.get(key)) for key in columns})
    return output.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON file containing editorial scorecards")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--csv-out", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = evaluate(data)
        json_text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        outputs = [(args.json_out, json_text), (args.csv_out, render_csv(result))]
        destinations = [path.resolve() for path, _ in outputs if path is not None]
        if args.input.resolve() in destinations or len(set(destinations)) != len(destinations):
            raise ValueError("input, JSON output, and CSV output must be different files")
        for path, _ in outputs:
            if path is not None and path.exists() and not args.overwrite:
                raise ValueError(f"output already exists: {path}; use --overwrite to replace")
        for path, content in outputs:
            if path is not None:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("w" if args.overwrite else "x", encoding="utf-8", newline="") as handle:
                    handle.write(content)
        if not destinations:
            # Escaped Unicode is valid JSON and survives redirected legacy Windows consoles.
            print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
        else:
            print(f"Calculated {result['ranked_count']} candidate rankings; "
                  f"{result['unranked_count']} entries unranked.")
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
