#!/usr/bin/env python3
"""Finish one generated triptych as a labeled 3840x2160 storyboard sheet."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH, HEIGHT = 3840, 2160
WHITE, INK, MUTED = "#ffffff", "#111111", "#555555"


def font(size):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def shorten(draw, value, max_width, face):
    value = " ".join(str(value).split())
    if draw.textlength(value, font=face) <= max_width:
        return value
    while value and draw.textlength(value + "…", font=face) > max_width:
        value = value[:-1]
    return value.rstrip() + "…"


def compose(board, manifest_dir, output):
    panels = board.get("panels", [])
    if not 1 <= len(panels) <= 3:
        raise ValueError("Each generated sheet must have 1 to 3 panels")
    ids = [panel["shot_id"] for panel in panels]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate shot IDs on one sheet")
    source = (manifest_dir / board["image"]).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    sheet = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(sheet)
    title_face, id_face, note_face, source_face = font(54), font(42), font(34), font(28)
    draw.text((80, 24), f'{board["board_id"]}  |  SCENE {board["scene_id"]}', font=title_face, fill=INK)

    art_box = (80, 100, WIDTH - 80, 1800)
    art_width = art_box[2] - art_box[0]
    art_height = art_box[3] - art_box[1]
    style = board.get("style", "monochrome")
    if style not in {"monochrome", "color"}:
        raise ValueError(f"Unsupported storyboard style: {style}")
    with Image.open(source) as original:
        artwork = ImageOps.exif_transpose(original).convert("RGB")
        if style == "monochrome":
            artwork = artwork.convert("L").convert("RGB")
    fitted = ImageOps.contain(artwork, (art_width, art_height), method=Image.Resampling.LANCZOS)
    art_x = art_box[0] + (art_width - fitted.width) // 2
    art_y = art_box[1] + (art_height - fitted.height) // 2
    sheet.paste(fitted, (art_x, art_y))
    draw.rectangle((art_x - 2, art_y - 2, art_x + fitted.width + 2, art_y + fitted.height + 2), outline=INK, width=3)
    draw.line((80, 1840, WIDTH - 80, 1840), fill=INK, width=3)

    column_width = (WIDTH - 160) // len(panels)
    for index, panel in enumerate(panels):
        x = 80 + index * column_width
        if index:
            draw.line((x - 15, 1870, x - 15, 2100), fill="#bbbbbb", width=2)
        available = column_width - 45
        draw.text((x, 1872), shorten(draw, f'{index + 1}  |  {panel["shot_id"]}', available, id_face), font=id_face, fill=INK)
        draw.text((x, 1940), shorten(draw, panel.get("camera", ""), available, note_face), font=note_face, fill=INK)
        draw.text((x, 2000), shorten(draw, panel.get("caption", ""), available, note_face), font=note_face, fill=MUTED)
        draw.text((x, 2070), shorten(draw, panel.get("source", ""), available, source_face), font=source_face, fill=MUTED)

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--board-id", help="Required if the manifest has multiple boards")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    boards = data.get("boards", [data])
    if args.board_id:
        boards = [board for board in boards if board.get("board_id") == args.board_id]
    if len(boards) != 1:
        raise ValueError("Select exactly one board with --board-id")
    boards[0].setdefault("style", data.get("style", "monochrome"))
    compose(boards[0], args.manifest.parent, args.output)
    print(f"Wrote {args.output} ({WIDTH}x{HEIGHT}, {len(boards[0]['panels'])} panels)")


if __name__ == "__main__":
    main()
