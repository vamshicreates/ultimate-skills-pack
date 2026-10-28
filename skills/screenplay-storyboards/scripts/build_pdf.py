#!/usr/bin/env python3
"""Build the final 16:9 PDF containing the shot list and every storyboard board."""

import argparse
import csv
import json
import re
from pathlib import Path

from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image, ImageOps


PAGE_W, PAGE_H = 960, 540  # Exactly 16:9 in PDF points.
MARGIN = 46


def register_fonts():
    choices = (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for path in choices:
        if Path(path).is_file():
            pdfmetrics.registerFont(TTFont("StoryboardText", path))
            return "StoryboardText"
    return "Helvetica"


class PDFBuilder:
    def __init__(self, output, title, font):
        self.pdf = canvas.Canvas(str(output), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
        self.pdf.setTitle(title)
        self.pdf.setAuthor("Screenplay Storyboards")
        self.font = font
        self.page_number = 0
        self.y = 0

    def cover(self, title, scenes, shots, boards):
        self.page_number += 1
        p = self.pdf
        p.setFillColorRGB(0.06, 0.06, 0.06)
        p.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        p.setFillColorRGB(0.98, 0.98, 0.98)
        p.setFont(self.font, 36)
        p.drawString(MARGIN, 355, "Screenplay Shot List")
        p.drawString(MARGIN, 306, "& Storyboards")
        p.setFillColorRGB(0.72, 0.72, 0.72)
        p.setFont(self.font, 17)
        p.drawString(MARGIN, 251, title[:80])
        p.setFont(self.font, 13)
        p.drawString(MARGIN, 110, f"{scenes} scenes   |   {shots} shots   |   {boards} storyboard boards")
        p.showPage()

    def start_text_page(self, section):
        self.page_number += 1
        p = self.pdf
        p.setFillColorRGB(1, 1, 1)
        p.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        p.setFillColorRGB(0.08, 0.08, 0.08)
        p.setFont(self.font, 17)
        p.drawString(MARGIN, PAGE_H - 45, section)
        p.setStrokeColorRGB(0.78, 0.78, 0.78)
        p.line(MARGIN, PAGE_H - 55, PAGE_W - MARGIN, PAGE_H - 55)
        p.setFont(self.font, 9)
        p.setFillColorRGB(0.45, 0.45, 0.45)
        p.drawRightString(PAGE_W - MARGIN, 24, str(self.page_number))
        self.y = PAGE_H - 84

    def write_text(self, path, section):
        self.start_text_page(section)
        content = path.read_text(encoding="utf-8")
        for raw in content.splitlines():
            if not raw.strip():
                self.y -= 8
                continue
            level = len(raw) - len(raw.lstrip("#"))
            if 1 <= level <= 3 and raw[level:level + 1] == " ":
                value = raw[level + 1:].strip()
                size = {1: 19, 2: 15, 3: 12}[level]
                leading = size + 6
                self.y -= 10
            else:
                value = raw.strip()
                size, leading = 10.5, 16
            value = re.sub(r"\*\*|`", "", value)
            if value.startswith("- "):
                value = "• " + value[2:]
            lines = simpleSplit(value, self.font, size, PAGE_W - 2 * MARGIN)
            for line in lines:
                if self.y < 45:
                    self.pdf.showPage()
                    self.start_text_page(section)
                self.pdf.setFillColorRGB(0.12, 0.12, 0.12)
                self.pdf.setFont(self.font, size)
                self.pdf.drawString(MARGIN, self.y, line)
                self.y -= leading
        self.pdf.showPage()

    def board(self, board_id, path):
        if not path.is_file():
            raise FileNotFoundError(path)
        self.page_number += 1
        self.pdf.bookmarkPage(board_id)
        self.pdf.addOutlineEntry(board_id, board_id, level=0)
        self.pdf.drawImage(ImageReader(str(path)), 0, 0, width=PAGE_W, height=PAGE_H)
        self.pdf.showPage()

    def reference(self, character, path, style="monochrome"):
        if not path.is_file():
            raise FileNotFoundError(path)
        self.page_number += 1
        p = self.pdf
        p.setFillColorRGB(1, 1, 1)
        p.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        name = character.get("name") or character["id"]
        p.setFillColorRGB(0.08, 0.08, 0.08)
        p.setFont(self.font, 19)
        p.drawString(MARGIN, PAGE_H - 46, f"Character reference: {name}"[:80])
        with Image.open(path) as source:
            picture = ImageOps.exif_transpose(source).convert("RGB")
            if style == "monochrome":
                picture = picture.convert("L").convert("RGB")
        max_w, max_h = PAGE_W - 2 * MARGIN, PAGE_H - 116
        scale = min(max_w / picture.width, max_h / picture.height)
        width, height = picture.width * scale, picture.height * scale
        p.drawImage(ImageReader(picture), (PAGE_W - width) / 2, 43 + (max_h - height) / 2, width=width, height=height)
        p.showPage()

    def save(self):
        self.pdf.save()


def build(root, output):
    manifest = json.loads((root / "storyboard_manifest.json").read_text(encoding="utf-8"))
    boards = manifest["boards"]
    if not boards:
        raise ValueError("No storyboard boards in manifest")
    with (root / "scene_ledger.csv").open(newline="", encoding="utf-8-sig") as stream:
        scenes = list(csv.DictReader(stream))
    shots = sum(len(board["panels"]) for board in boards)
    title = manifest.get("title") or root.name.replace("_", " ").replace("-", " ").title()
    builder = PDFBuilder(output, title, register_fonts())
    builder.cover(title, len(scenes), shots, len(boards))
    builder.write_text(root / "continuity_bible.md", "Character & Visual Continuity")
    style = manifest.get("style", "monochrome")
    if style not in {"monochrome", "color"}:
        raise ValueError(f"Unsupported storyboard style: {style}")
    for character in manifest.get("characters", []):
        builder.reference(character, root / character["reference_image"], style)
    builder.write_text(root / "shot_list.md", "Scene-by-Scene Shot List")
    for board in boards:
        board_id = board["board_id"]
        compact = root / "boards" / f"{board_id}.jpg"
        builder.board(board_id, compact if compact.is_file() else root / "boards" / f"{board_id}.png")
    builder.save()
    print(f"Wrote {output} with {len(boards)} storyboard board pages")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.project / "storyboards.pdf"
    build(args.project, output)


if __name__ == "__main__":
    main()
