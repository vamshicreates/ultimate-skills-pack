#!/usr/bin/env python3
"""Validate an AI-authored film breakdown and export local review reports."""

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path


CATEGORIES = (
    "locations", "cast", "costume", "props", "vehicles", "animals",
    "background", "special_equipment", "vfx", "stunts", "makeup_hair",
    "art_set", "sound", "weather", "practical_effects", "lighting",
)
STATES = {"present", "none_identified", "not_assessed"}
PARTICIPATION = {
    "visible_speaking", "visible_non_speaking", "off_screen_voice",
    "voice_over", "referenced_only", "uncertain",
}


class InvalidBreakdown(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidBreakdown(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def index_rows(data, key):
    rows = data.get(key)
    require(isinstance(rows, list), f"{key} must be an array")
    result = {}
    for row in rows:
        require(isinstance(row, dict) and nonempty(row.get("id")),
                f"{key}: each record needs a nonempty id")
        require(row["id"] not in result, f"{key}: duplicate id {row['id']}")
        result[row["id"]] = row
    return result


def refs(values, known, label, minimum=0):
    require(isinstance(values, list) and len(values) >= minimum,
            f"{label}: expected array with at least {minimum} references")
    require(all(isinstance(v, str) and v in known for v in values),
            f"{label}: unknown reference")
    require(len(values) == len(set(values)), f"{label}: repeated reference")


def evidence(row, units, minimum=1):
    items = row.get("evidence")
    require(isinstance(items, list) and len(items) >= minimum,
            f"{row['id']}: evidence array needs at least {minimum} entries")
    for item in items:
        require(isinstance(item, dict), f"{row['id']}: invalid evidence")
        require(item.get("unit_id") in units, f"{row['id']}: unknown source unit")
        require(nonempty(item.get("anchor")) and nonempty(item.get("excerpt")),
                f"{row['id']}: evidence needs anchor and exact excerpt")


def status_evidence(row, units):
    require(row.get("status") in {"explicit", "inferred", "question"},
            f"{row['id']}: invalid evidence status")
    evidence(row, units)
    if row["status"] == "inferred":
        require(nonempty(row.get("rationale")), f"{row['id']}: inference needs rationale")


def validate(data):
    require(isinstance(data, dict), "Root must be an object")
    require(data.get("schema_version") == "1.0", "Unsupported schema_version")
    film, source, scope = (data.get(key) for key in ("film", "source", "scope"))
    require(isinstance(film, dict) and nonempty(film.get("title")), "Missing film title")
    require("revision" in film, "film.revision is required; use null if unknown")
    require(film.get("lock_status") in {"confirmed", "unconfirmed"}, "Invalid lock_status")
    require(isinstance(source, dict), "Missing source object")
    require(nonempty(source.get("filename")), "Missing source filename")
    require(isinstance(source.get("sha256"), str) and
            re.fullmatch(r"[0-9a-f]{64}", source["sha256"]), "Invalid source SHA-256")
    require(nonempty(source.get("extraction_method")), "Missing extraction method")
    require(isinstance(source.get("languages"), list) and source["languages"] and
            all(nonempty(v) for v in source["languages"]), "Missing source languages")
    require(isinstance(source.get("warnings"), list) and
            all(nonempty(v) for v in source["warnings"]), "source.warnings must be strings")
    units = index_rows(source, "units")
    require(units, "No source units recorded")
    for unit in units.values():
        require(nonempty(unit.get("locator")), f"{unit['id']}: missing locator")
        require(type(unit.get("readable")) is bool and type(unit.get("reviewed")) is bool,
                f"{unit['id']}: readable and reviewed must be booleans")
        require(not unit["reviewed"] or unit["readable"],
                f"{unit['id']}: unreadable material cannot be reviewed")
    scenes = index_rows(data, "scenes")
    entities = index_rows(data, "entities")
    requirements = index_rows(data, "requirements")
    continuity = index_rows(data, "continuity")
    questions = index_rows(data, "questions")
    require(scenes, "No scenes inventoried")
    require(isinstance(scope, dict) and scope.get("mode") in {"full", "sample", "selected"},
            "Invalid scope mode")
    refs(scope.get("scene_ids"), scenes, "scope.scene_ids",
         minimum=0 if scope["mode"] == "full" else 1)
    cats = scope.get("categories")
    require(isinstance(cats, list) and bool(cats), "Missing scope categories")
    require(cats == ["all"] or (all(c in CATEGORIES for c in cats) and
            len(cats) == len(set(cats))), "Invalid scope categories")
    requested_cats = CATEGORIES if cats == ["all"] else cats
    requested_scenes = scenes if scope["mode"] == "full" else scope["scene_ids"]

    for scene in scenes.values():
        require("printed_number" in scene and "script_time" in scene,
                f"{scene['id']}: printed_number and script_time required (null if unknown)")
        require(nonempty(scene.get("slugline")) and nonempty(scene.get("summary")),
                f"{scene['id']}: missing slugline or summary")
        require(scene.get("int_ext") in {"INT", "EXT", "INT/EXT", "EXT/INT", "UNKNOWN"},
                f"{scene['id']}: invalid int_ext")
        refs(scene.get("source_unit_ids"), units, scene["id"], minimum=1)
        states = scene.get("category_status")
        require(isinstance(states, dict) and set(states) == set(CATEGORIES) and
                all(v in STATES for v in states.values()), f"{scene['id']}: invalid category_status")
        if scene.get("parent_scene_id") is not None:
            require(scene["parent_scene_id"] in scenes and scene["parent_scene_id"] != scene["id"],
                    f"{scene['id']}: invalid parent_scene_id")
    for entity in entities.values():
        require(entity.get("category") in CATEGORIES and nonempty(entity.get("name")),
                f"{entity['id']}: invalid category or name")
        require(isinstance(entity.get("aliases"), list) and
                all(nonempty(a) for a in entity["aliases"]), f"{entity['id']}: aliases must be strings")

    seen = Counter()
    for row in requirements.values():
        require(row.get("scene_id") in scenes and row.get("category") in CATEGORIES,
                f"{row['id']}: invalid scene/category")
        require(nonempty(row.get("description")), f"{row['id']}: missing description")
        for field in ("entity_id", "quantity", "quantity_unit"):
            require(field in row, f"{row['id']}: missing {field}; use null if unknown")
        if row["entity_id"] is not None:
            require(row["entity_id"] in entities and
                    entities[row["entity_id"]]["category"] == row["category"],
                    f"{row['id']}: entity missing or category mismatch")
        if row.get("subject_entity_id") is not None:
            require(row["subject_entity_id"] in entities, f"{row['id']}: unknown subject entity")
        quantity = row["quantity"]
        require(quantity is None or (type(quantity) in (int, float) and
                math.isfinite(quantity) and quantity >= 0), f"{row['id']}: invalid quantity")
        if quantity is not None:
            require(nonempty(row["quantity_unit"]), f"{row['id']}: quantity needs a unit")
        if row["category"] == "cast":
            require(row.get("participation") in PARTICIPATION,
                    f"{row['id']}: missing/invalid cast participation")
        status_evidence(row, units)
        seen[(row["scene_id"], row["category"])] += 1
    for scene in scenes.values():
        for cat, state in scene["category_status"].items():
            require((state == "present") == (seen[(scene["id"], cat)] > 0),
                    f"{scene['id']}/{cat}: assessment and requirements disagree")
    for row in continuity.values():
        refs(row.get("scene_ids"), scenes, row["id"], minimum=2)
        require(all(nonempty(row.get(k)) for k in ("element", "dependency", "department")),
                f"{row['id']}: missing continuity description/owner")
        if row.get("entity_id") is not None:
            require(row["entity_id"] in entities, f"{row['id']}: unknown continuity entity")
        status_evidence(row, units)
    for row in questions.values():
        refs(row.get("scene_ids"), scenes, row["id"])
        require(nonempty(row.get("department")) and nonempty(row.get("question")),
                f"{row['id']}: missing question/owner")
        evidence(row, units, minimum=0)
        if row.get("requirement_id") is not None:
            require(row["requirement_id"] in requirements, f"{row['id']}: unknown requirement")

    gaps = [u["id"] for u in units.values() if not (u["readable"] and u["reviewed"])]
    unassessed = [f"{sid}/{cat}" for sid in requested_scenes for cat in requested_cats
                  if scenes[sid]["category_status"][cat] == "not_assessed"]
    return {"complete_for_requested_scope": not gaps and not unassessed,
            "source_gaps": gaps, "unassessed": unassessed,
            "scenes": len(scenes), "requirements": len(requirements), "questions": len(questions)}


def cell(value):
    if value is None:
        return ""
    text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
    # Treat screenplay/vendor text as data when opened in spreadsheet applications.
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")) else text


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows({key: cell(row.get(key)) for key in fields} for row in rows)


def build_reports(data, out, coverage):
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "scene-inventory.csv",
              ["id", "printed_number", "slugline", "source_unit_ids", "int_ext", "script_time",
               "summary", "story_day", "parent_scene_id", "category_status", "notes"], data["scenes"])
    write_csv(out / "scene-requirements.csv",
              ["id", "scene_id", "entity_id", "category", "description", "status", "evidence",
               "rationale", "quantity", "quantity_unit", "participation", "subject_entity_id", "notes"],
              data["requirements"])
    write_csv(out / "entity-register.csv", ["id", "category", "name", "aliases", "actor_name", "notes"],
              data["entities"])
    write_csv(out / "continuity-dependencies.csv",
              ["id", "scene_ids", "entity_id", "element", "dependency", "department", "status",
               "evidence", "rationale", "notes"], data["continuity"])
    write_csv(out / "review-questions.csv",
              ["id", "scene_ids", "department", "question", "evidence", "requirement_id"], data["questions"])
    lines = [f"# {data['film']['title']} — production breakdown", "",
             f"Source: {data['source']['filename']}",
             f"Revision: {data['film']['revision'] or 'Unknown'}; lock: {data['film']['lock_status']}",
             f"Scope: {data['scope']['mode']}; categories: {', '.join(data['scope']['categories'])}",
             f"Extraction coverage: {'complete for requested scope' if coverage['complete_for_requested_scope'] else 'PARTIAL'}.",
             f"Inventoried scenes: {coverage['scenes']}; requirements: {coverage['requirements']}; open questions: {coverage['questions']}.",
             "", "Counts describe this inventory; scenes are not shoot days and story locations are not booked venues.",
             "Department review remains required.", "", "## Requirements by category", "",
             "| Category | Requirement records | Linked unique entities |", "| --- | ---: | ---: |"]
    for cat in CATEGORIES:
        rows = [r for r in data["requirements"] if r["category"] == cat]
        linked = {r["entity_id"] for r in rows if r["entity_id"] is not None}
        lines.append(f"| {cat} | {len(rows)} | {len(linked)} |")
    referenced = sum(r.get("participation") == "referenced_only" for r in data["requirements"])
    lines += ["", f"Referenced-only cast records: {referenced}; exclude these from on-set cast requirements.",
              "", "## Coverage gaps and source warnings", ""]
    issues = ([f"Unread/unreadable source unit: {u}" for u in coverage["source_gaps"]] +
              [f"Unassessed: {item}" for item in coverage["unassessed"]] + data["source"]["warnings"])
    lines += [f"- {issue}" for issue in issues] or ["No coverage gaps or source warnings recorded."]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        coverage = validate(data)
        if not args.validate_only:
            build_reports(data, args.out or args.input.parent / "reports", coverage)
        print(json.dumps(coverage, ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Breakdown validation/export failed: {exc}\n")


if __name__ == "__main__":
    main()
