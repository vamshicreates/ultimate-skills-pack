#!/usr/bin/env python3
"""Create a detailed scene-by-scene sound breakdown PDF from a JSON cue sheet.

Usage: python3 build_breakdown_pdf.py --sheet cue_sheet.json --out breakdown.pdf
Requires ReportLab. The JSON schema is described in the adjacent SKILL.md.
"""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer


CATEGORIES = (
    ("music", "Music"),
    ("foley", "Foley"),
    ("ambience", "Ambience"),
    ("sfx", "Sound effects and transitions"),
    ("silence", "Intentional silence"),
)
CUE_FIELDS = (
    ("time", "Time / frames"),
    ("sync", "Sync event"),
    ("description", "Sound design"),
    ("method", "Generation / source"),
    ("mix", "Mix notes"),
    ("status", "Status"),
    ("asset", "Delivered file"),
)


def paragraph_text(value: object) -> str:
    return escape(str(value)).replace("\n", "<br/>")


def add_label(story: list, label: str, value: object, style: ParagraphStyle) -> None:
    story.append(Paragraph(f"<b>{escape(label)}:</b> {paragraph_text(value)}", style))


def footer(canvas, document) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#526173"))
    canvas.drawRightString(width - 18 * mm, 13 * mm, f"Page {document.page}")
    canvas.restoreState()


def build(sheet: dict, destination: Path, assets_root: Path | None = None) -> None:
    if not sheet.get("film_title") or not isinstance(sheet.get("scenes"), list) or not sheet["scenes"]:
        raise ValueError("Cue sheet needs film_title and a nonempty scenes list")
    styles = getSampleStyleSheet()
    title = ParagraphStyle("FilmTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=19, leading=23, spaceAfter=10)
    scene_title = ParagraphStyle("SceneTitle", parent=styles["Heading1"], fontSize=14, leading=18, spaceAfter=8)
    category_title = ParagraphStyle("CategoryTitle", parent=styles["Heading2"], fontSize=11, leading=14, textColor=colors.HexColor("#164A69"), spaceBefore=10, spaceAfter=5)
    cue_title = ParagraphStyle("CueTitle", parent=styles["Heading3"], fontSize=9.5, leading=12, spaceAfter=3)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=8.5, leading=12, alignment=TA_LEFT, spaceAfter=3)
    small = ParagraphStyle("Small", parent=body, fontSize=8, leading=11)

    story = [Paragraph(paragraph_text(sheet["film_title"]), title), Paragraph("Scene-by-scene sound breakdown", styles["Heading2"]), Spacer(1, 6)]
    for key, label in (("source_file", "Picture master"), ("frame_rate", "Frame rate"), ("duration", "Duration"), ("version", "Breakdown version")):
        if sheet.get(key):
            add_label(story, label, sheet[key], body)
    story.append(Spacer(1, 8))
    add_label(story, "Scenes", len(sheet["scenes"]), body)
    story.append(Paragraph("Each cue lists its timing, purpose, creation method, mix direction, status, and delivered file path.", body))

    seen_scene_ids: set[str] = set()
    seen_cue_ids: set[str] = set()
    for scene in sheet["scenes"]:
        scene_id = str(scene["id"])
        if scene_id in seen_scene_ids:
            raise ValueError(f"Duplicate scene ID: {scene_id}")
        seen_scene_ids.add(scene_id)
        story.append(PageBreak())
        story.append(Paragraph(f"{paragraph_text(scene_id)} - {paragraph_text(scene['name'])}", scene_title))
        for key, label in (("time", "Scene range"), ("picture", "Visible action"), ("production_audio", "Dialogue / production audio"), ("sound_direction", "Sound direction")):
            if not scene.get(key):
                raise ValueError(f"{scene_id} needs {key}")
            add_label(story, label, scene[key], body)
        story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#A6B3BC"), spaceBefore=8, spaceAfter=5))
        for key, label in CATEGORIES:
            if key not in scene:
                raise ValueError(f"{scene_id} needs a {key} section (use an empty list with a reason if absent)")
            section = scene[key]
            if not isinstance(section, dict) or not isinstance(section.get("cues"), list):
                raise ValueError(f"{scene_id}.{key} needs a cues list")
            story.append(Paragraph(label, category_title))
            if not section["cues"]:
                if not section.get("none_reason"):
                    raise ValueError(f"{scene_id}.{key} needs none_reason when there are no cues")
                add_label(story, "None", section["none_reason"], small)
                continue
            for cue in section["cues"]:
                cue_id = str(cue["id"])
                if cue_id in seen_cue_ids:
                    raise ValueError(f"Duplicate cue ID: {cue_id}")
                seen_cue_ids.add(cue_id)
                missing = [field for field in ("name", "time", "sync", "description", "method", "mix", "status") if not cue.get(field)]
                if missing or (key != "silence" and not cue.get("asset")):
                    raise ValueError(f"{cue_id} missing {', '.join(missing or ['asset'])}")
                if assets_root is not None and cue.get("asset"):
                    root = assets_root.resolve()
                    relative = Path(cue["asset"])
                    asset = (root / relative).resolve()
                    if relative.is_absolute() or not asset.is_relative_to(root) or not asset.is_file():
                        raise ValueError(f"{cue_id} asset is missing or outside assets root: {relative}")
                block = [Paragraph(f"{paragraph_text(cue_id)} - {paragraph_text(cue['name'])}", cue_title)]
                for field, field_label in CUE_FIELDS:
                    if cue.get(field):
                        add_label(block, field_label, cue[field], small)
                block.append(Spacer(1, 5))
                story.append(KeepTogether(block))

    destination.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(destination), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=20 * mm, title=f"{sheet['film_title']} sound breakdown")
    document.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--assets-root", type=Path, help="validate all delivered asset paths against this package folder")
    arguments = parser.parse_args()
    build(json.loads(arguments.sheet.read_text()), arguments.out, arguments.assets_root)


if __name__ == "__main__":
    main()
