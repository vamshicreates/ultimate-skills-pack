#!/usr/bin/env python3
"""Inspect screenshots and package selected frames as a Canva carousel import."""

import argparse
import json
import math
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
PAGE_W, PAGE_H, PANEL_H = 1080, 1350, 450


def images_in(folder: Path) -> list[Path]:
    return sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS), key=lambda p: p.name)


def cover_preview(image: Image.Image, width: int, height: int, fx: float = 50, fy: float = 50) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    ratio = max(width / image.width, height / image.height)
    scaled = image.resize((math.ceil(image.width * ratio), math.ceil(image.height * ratio)), Image.Resampling.LANCZOS)
    left = round((scaled.width - width) * fx / 100)
    top = round((scaled.height - height) * fy / 100)
    return scaled.crop((left, top, left + width, top + height))


def contact(folder: Path, output: Path) -> None:
    files = images_in(folder)
    if not files:
        raise ValueError(f"No supported images in {folder}")
    thumb_w, thumb_h, label_h, columns = 300, 125, 32, 4
    sheet = Image.new("RGB", (columns * thumb_w, math.ceil(len(files) / columns) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(files):
        with Image.open(path) as source:
            preview = cover_preview(source, thumb_w, thumb_h)
        x, y = index % columns * thumb_w, index // columns * (thumb_h + label_h)
        sheet.paste(preview, (x, y))
        draw.text((x + 4, y + thumb_h + 4), f"{index + 1:02d} {path.name[:34]}", fill="black")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=88)
    print(f"Contact sheet: {output} ({len(files)} images)")


def parse_item(item: object, folder: Path) -> tuple[Path, float, float]:
    if isinstance(item, str):
        name, fx, fy = item, 50.0, 50.0
    elif isinstance(item, dict):
        name, fx, fy = item.get("file"), float(item.get("focus_x", 50)), float(item.get("focus_y", 50))
    else:
        raise ValueError("Manifest items must be filenames or objects with a file key")
    if not isinstance(name, str) or not 0 <= fx <= 100 or not 0 <= fy <= 100:
        raise ValueError(f"Invalid image item: {item!r}")
    path = (folder / name).resolve()
    if not path.is_relative_to(folder.resolve()) or not path.is_file() or path.suffix.lower() not in EXTENSIONS:
        raise ValueError(f"Invalid or missing image: {name}")
    return path, fx, fy


def build(folder: Path, manifest: Path, output: Path, max_width: int, quality: int) -> None:
    slides = json.loads(manifest.read_text(encoding="utf-8")).get("slides")
    if not isinstance(slides, list) or not slides or any(not isinstance(slide, list) or len(slide) != 3 for slide in slides):
        raise ValueError("Manifest must contain nonempty slides, each with exactly three images")
    chosen = [[parse_item(item, folder) for item in slide] for slide in slides]
    source_paths = [path for slide in chosen for path, _, _ in slide]
    if len(source_paths) != len(set(source_paths)):
        raise ValueError("Each source image may appear only once")
    if output.exists():
        raise ValueError(f"Output directory already exists: {output}")
    assets = output / "assets"
    assets.mkdir(parents=True)
    sections = []
    preview = Image.new("RGB", (PAGE_W, PAGE_H * len(chosen)), "white")
    for page_no, slide in enumerate(chosen, 1):
        panels = []
        for panel_no, (path, fx, fy) in enumerate(slide, 1):
            asset = f"{page_no:02d}-{panel_no}.jpg"
            with Image.open(path) as source:
                source = ImageOps.exif_transpose(source).convert("RGB")
                if source.width > max_width:
                    source.thumbnail((max_width, max_width * 10), Image.Resampling.LANCZOS)
                source.save(assets / asset, "JPEG", quality=quality, optimize=True)
                preview.paste(cover_preview(source, PAGE_W, PANEL_H, fx, fy), (0, (page_no - 1) * PAGE_H + (panel_no - 1) * PANEL_H))
            panels.append(f'<div class="panel"><img src="assets/{asset}" alt="" style="object-position:{fx:g}% {fy:g}%"></div>')
        sections.append(f'<section class="page" data-document-role="page" data-label="Slide {page_no}">{"".join(panels)}</section>')
    document = (
        '<!doctype html><html><head><meta charset="utf-8"><title>Photo carousel</title>'
        '<style>*{box-sizing:border-box}html,body{margin:0;padding:0}.page{width:1080px;height:1350px;overflow:hidden;'
        'display:grid;grid-template-rows:repeat(3,450px);break-after:page;page-break-after:always}'
        '.panel{width:1080px;height:450px;overflow:hidden}.panel img{display:block;width:1080px;height:450px;object-fit:cover}'
        '</style></head><body>' + "".join(sections) + '</body></html>'
    )
    (output / "index.html").write_text(document, encoding="utf-8")
    preview.save(output / "preview.jpg", quality=82)
    archive = output / "carousel-import.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(output / "index.html", "index.html")
        for asset in sorted(assets.iterdir()):
            bundle.write(asset, f"assets/{asset.name}")
    print(f"ZIP: {archive} ({archive.stat().st_size / 1_000_000:.2f} MB); pages: {len(chosen)}; preview: {output / 'preview.jpg'}")
    if archive.stat().st_size >= 10_000_000:
        print("WARNING: ZIP is at least 10 MB; rebuild with smaller --max-width or --quality")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("contact", help="Make a cropped contact sheet for visual selection")
    inspect.add_argument("--folder", type=Path, required=True)
    inspect.add_argument("--output", type=Path, required=True)
    create = commands.add_parser("build", help="Build an HTML+assets ZIP for Canva import")
    create.add_argument("--folder", type=Path, required=True)
    create.add_argument("--manifest", type=Path, required=True)
    create.add_argument("--output-dir", type=Path, required=True)
    create.add_argument("--max-width", type=int, default=1440)
    create.add_argument("--quality", type=int, default=78)
    args = parser.parse_args()
    if args.command == "contact":
        contact(args.folder, args.output)
    else:
        if args.max_width < PAGE_W or not 1 <= args.quality <= 95:
            parser.error("--max-width must be at least 1080 and --quality must be 1–95")
        build(args.folder, args.manifest, args.output_dir, args.max_width, args.quality)


if __name__ == "__main__":
    main()
