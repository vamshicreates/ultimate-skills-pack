#!/usr/bin/env python3
"""Check scene, shot, frame, and board bookkeeping for a storyboard project."""

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from PIL import Image, ImageChops
from pypdf import PdfReader


SHOT_ID = re.compile(r"S\d+-SH\d+")


def validate(root, final=False):
    errors = []
    ledger_path = root / "scene_ledger.csv"
    manifest_path = root / "storyboard_manifest.json"
    shot_list_path = root / "shot_list.md"
    with ledger_path.open(newline="", encoding="utf-8-sig") as stream:
        scenes = list(csv.DictReader(stream))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    boards = manifest["boards"]
    characters = manifest.get("characters", [])
    shot_list_ids = set(SHOT_ID.findall(shot_list_path.read_text(encoding="utf-8")))
    scene_ids = [row["scene_id"] for row in scenes]
    if len(scene_ids) != len(set(scene_ids)):
        errors.append("Duplicate scene ID in ledger")
    board_ids, panel_ids = [], []
    shots_by_scene, boards_by_scene = Counter(), Counter()
    for board in boards:
        scene_id, board_id = board["scene_id"], board["board_id"]
        board_ids.append(board_id)
        boards_by_scene[scene_id] += 1
        if scene_id not in scene_ids:
            errors.append(f"{board_id}: scene missing from ledger")
        panels = board.get("panels", [])
        if not 1 <= len(panels) <= 3:
            errors.append(f"{board_id}: must contain 1 to 3 panels")
        if final:
            board_path = root / "boards" / f"{board_id}.png"
            if not board_path.is_file():
                errors.append(f"{board_id}: board image missing")
            else:
                with Image.open(board_path) as image:
                    if image.size != (3840, 2160):
                        errors.append(f"{board_id}: board is not 3840x2160")
                    style = board.get("style", manifest.get("style", "monochrome"))
                    if style not in {"monochrome", "color"}:
                        errors.append(f"{board_id}: unsupported style {style}")
                    if style == "monochrome":
                        red, green, blue = image.convert("RGB").split()
                        if ImageChops.difference(red, green).getbbox() or ImageChops.difference(green, blue).getbbox():
                            errors.append(f"{board_id}: board contains color")
            if not (root / board["image"]).is_file():
                errors.append(f"{board_id}: generated triptych image missing")
        for panel in panels:
            shot_id = panel["shot_id"]
            panel_ids.append(shot_id)
            shots_by_scene[scene_id] += 1
            if not shot_id.startswith(scene_id + "-SH"):
                errors.append(f"{shot_id}: shot ID does not match scene {scene_id}")
            if shot_id not in shot_list_ids:
                errors.append(f"{shot_id}: missing from shot list")
            if not panel.get("source") or not panel.get("camera") or not panel.get("caption"):
                errors.append(f"{shot_id}: missing source, camera, or caption")
    if len(board_ids) != len(set(board_ids)):
        errors.append("Duplicate board ID")
    if len(panel_ids) != len(set(panel_ids)):
        errors.append("Duplicate shot ID in manifest")
    character_ids = [character["id"] for character in characters]
    if len(character_ids) != len(set(character_ids)):
        errors.append("Duplicate character ID in manifest")
    if final:
        for character in characters:
            if not (root / character["reference_image"]).is_file():
                errors.append(f"{character['id']}: reference image missing")
    for shot_id in shot_list_ids - set(panel_ids):
        errors.append(f"{shot_id}: no storyboard panel")
    for row in scenes:
        scene_id = row["scene_id"]
        for column, actual in (("shot_count", shots_by_scene[scene_id]), ("board_count", boards_by_scene[scene_id])):
            try:
                expected = int(row[column])
            except (ValueError, KeyError):
                errors.append(f"{scene_id}: invalid {column}")
            else:
                if expected != actual:
                    errors.append(f"{scene_id}: {column} is {expected}, found {actual}")
        if final and row.get("status") != "verified":
            errors.append(f"{scene_id}: status is not verified")
    if final:
        plan_path = root / "production_plan.json"
        if not plan_path.is_file():
            errors.append("production_plan.json is missing")
        else:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            expected = {
                "scene_count": len(scenes),
                "shot_count": len(panel_ids),
                "board_count": len(boards),
            }
            for key, value in expected.items():
                if plan.get(key) != value:
                    errors.append(f"Production plan {key} does not match project")
            if plan.get("confirmed") is not True:
                errors.append("Production plan has no recorded user confirmation")
            try:
                if plan.get("image_call_mode") == "per_shot":
                    baseline = plan["shot_count"] + plan["reference_image_count"]
                else:
                    baseline = plan["board_count"] + plan["reference_image_count"]
                ceiling = plan["approved_max_calls"]
                actual = plan["actual_calls"]
                allowance = plan["correction_call_allowance"]
                if ceiling != baseline + allowance:
                    errors.append("Approved call ceiling does not match baseline plus corrections")
                if not baseline <= actual <= ceiling:
                    errors.append("Actual image calls are outside the approved range")
            except (KeyError, TypeError):
                errors.append("Production plan call counts are incomplete")
        pdf_path = root / "storyboards.pdf"
        if not pdf_path.is_file():
            errors.append("Final storyboards.pdf is missing")
        else:
            pdf = PdfReader(str(pdf_path))
            if len(pdf.pages) < len(boards) + len(characters) + 3:
                errors.append("PDF has too few pages for cover, text, references, and boards")
            for index, page in enumerate(pdf.pages):
                if float(page.mediabox.width) * 9 != float(page.mediabox.height) * 16:
                    errors.append(f"PDF page {index + 1} is not 16:9")
            for board, page in zip(boards, pdf.pages[-len(boards):]):
                if not list(page.images):
                    errors.append(f"{board['board_id']}: PDF board page has no image")
            if sum(bool(list(page.images)) for page in pdf.pages) < len(boards) + len(characters):
                errors.append("PDF does not contain every board and character reference page")
    return errors, len(scenes), len(panel_ids), len(boards)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--final", action="store_true", help="Require verified scenes and output files")
    args = parser.parse_args()
    errors, scenes, shots, boards = validate(args.project, args.final)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)
    print(f"Validated {scenes} scenes, {shots} shots, {boards} boards")


if __name__ == "__main__":
    main()
