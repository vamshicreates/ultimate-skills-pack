#!/usr/bin/env python3
"""Build matching Telugu and English Canva import ZIPs with Python's standard library."""

from __future__ import annotations

import argparse
import json
import shutil
from html import escape
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {"te": "Telugu", "en": "English"}
REQUIRED_COPY = (
    "category", "cover_headline_lines", "cover_subhead", "detail_headline_lines",
    "detail_points", "detail_qualifier", "closing_tag", "closing_headline_lines",
    "closing_body", "source_label", "cta_tag", "cta_headline_lines", "cta_body",
)


def fail(message: str) -> None:
    raise SystemExit(message)


def e(value: str) -> str:
    return escape(value, quote=True)


def lines(values: list[str]) -> str:
    if not isinstance(values, list) or not (1 <= len(values) <= 3) or not all(
        isinstance(v, str) and v.strip() for v in values
    ):
        fail("Headline lines must be a list of 1–3 nonempty strings")
    return "<br>".join(e(v.strip()) for v in values)


def validate(data: dict, image: Path | None, screenshot: Path | None) -> None:
    if image is not None and not image.is_file():
        fail(f"Cover image not found: {image}")
    if screenshot is not None and not screenshot.is_file():
        fail(f"Source screenshot not found: {screenshot}")
    source = data.get("source_url")
    if source:
        if not isinstance(source, str):
            fail("source_url must be an HTTP(S) URL")
        parsed = urlparse(source)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            fail("source_url must be an HTTP(S) URL")
    elif screenshot is None:
        fail("Provide source_url in the story JSON or pass --screenshot")
    if not isinstance(data.get("copy"), dict) or set(data["copy"]) != set(LANGUAGES):
        fail("copy must contain exactly te and en")
    for lang, copy in data["copy"].items():
        for key in REQUIRED_COPY:
            if key not in copy:
                fail(f"Missing copy.{lang}.{key}")
        for key in ("cover_headline_lines", "detail_headline_lines", "closing_headline_lines", "cta_headline_lines"):
            lines(copy[key])
        if not isinstance(copy["detail_points"], list) or len(copy["detail_points"]) != 3:
            fail(f"copy.{lang}.detail_points must contain exactly three points")
        if not all(isinstance(x, str) and x.strip() for x in copy["detail_points"]):
            fail(f"copy.{lang}.detail_points contains an empty point")
        for key in REQUIRED_COPY:
            if key.endswith("_lines") or key == "detail_points":
                continue
            if not isinstance(copy[key], str) or not copy[key].strip():
                fail(f"copy.{lang}.{key} must be nonempty text")


def page_footer() -> str:
    return ('<div class="footer"><div class="footer-shape" aria-hidden="true"></div>'
            '<img src="assets/instagram-white.png" alt="Instagram">'
            '<span class="footer-text">@utvhottnewsapp</span></div>')


def render(lang: str, data: dict, image_name: str | None) -> str:
    copy = data["copy"][lang]
    css = (ROOT / "assets" / "styles.css").read_text(encoding="utf-8")
    points = "\n".join(
        f'<div class="point"><div class="point-shape" aria-hidden="true"></div>'
        f'<div class="number-shape" aria-hidden="true"></div>'
        f'<span class="number-text">{n}</span><span class="point-text">{e(point)}</span></div>'
        for n, point in enumerate(copy["detail_points"], 1)
    )
    cover_media = (f'<img class="cover-photo" src="assets/{e(image_name)}" alt="Article lead image">\n'
                   '  <div class="cover-shade"></div>' if image_name else
                   '<div class="cover-art" aria-hidden="true"></div>')
    cover_class = "cover" if image_name else "cover cover-text-only"
    return f'''<!doctype html>
<html lang="{lang}">
<head><meta charset="utf-8"><meta name="viewport" content="width=1080, initial-scale=1">
<title>UTV Hott News | {e(" ".join(copy["cover_headline_lines"]))}</title>
<style>{css}</style></head>
<body>
<section class="page {cover_class}" data-document-role="page" data-label="Cover">
  {cover_media}
  <img class="logo" src="assets/logo.png" alt="UTV Hott News logo">
  <div class="cover-copy"><div class="pill"><div class="pill-shape" aria-hidden="true"></div><span class="pill-text">{e(copy["category"])}</span></div>
  <h1>{lines(copy["cover_headline_lines"])}</h1>
  <p class="subhead">{e(copy["cover_subhead"])}</p></div>
  {page_footer()}
</section>
<section class="page detail" data-document-role="page" data-label="Discussion points">
  <img class="logo" src="assets/logo.png" alt="UTV Hott News logo">
  <div class="topline"></div>
  <div class="detail-content"><div class="section-tag">{'ముఖ్యాంశాలు' if lang == 'te' else 'KEY POINTS'}</div>
  <h2>{lines(copy["detail_headline_lines"])}</h2><div class="red-rule"></div>
  <div class="point-list">{points}</div>
  <p class="qualifier">{e(copy["detail_qualifier"])}</p></div>
  {page_footer()}
</section>
<section class="page closing" data-document-role="page" data-label="Context">
  <div class="closing-top-accent" aria-hidden="true"></div>
  <div class="closing-content"><div class="section-tag"><div class="tag-shape" aria-hidden="true"></div><span class="tag-text">{e(copy["closing_tag"])}</span></div>
  <h2>{lines(copy["closing_headline_lines"])}</h2><div class="divider"></div>
  <p class="body">{e(copy["closing_body"])}</p></div>
  <p class="source">{e(copy["source_label"])}</p>
  <img class="logo" src="assets/logo.png" alt="UTV Hott News logo">
  {page_footer()}
</section>
<section class="page cta" data-document-role="page" data-label="Download app">
  <img class="logo" src="assets/logo.png" alt="UTV Hott News logo">
  <div class="topline"></div>
  <div class="cta-content"><div class="section-tag">{e(copy["cta_tag"])}</div>
  <h2>{lines(copy["cta_headline_lines"])}</h2>
  <div class="red-rule"></div>
  <p class="cta-body">{e(copy["cta_body"])}</p>
  <div class="download-box"><div class="download-shape" aria-hidden="true"></div><strong class="download-title">UTV Hott News App</strong><span class="download-action">{'ఇప్పుడే డౌన్‌లోడ్ చేసుకోండి' if lang == 'te' else 'Download now'}</span></div>
  <img class="store-badges" src="assets/store-badges.svg" alt="Download on the App Store and Get it on Google Play"></div>
  {page_footer()}
</section>
</body></html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--story", required=True, type=Path, help="Bilingual story JSON")
    parser.add_argument("--image", type=Path, help="Optional usable cover photo")
    parser.add_argument("--screenshot", type=Path, help="Source screenshot; required if story has no source_url")
    parser.add_argument("--output", required=True, type=Path, help="New output directory")
    args = parser.parse_args()
    if args.output.exists():
        fail(f"Output directory already exists: {args.output}")
    data = json.loads(args.story.read_text(encoding="utf-8"))
    validate(data, args.image, args.screenshot)
    args.output.mkdir(parents=True)
    image_name = "article" + args.image.suffix.lower() if args.image else None
    for lang in LANGUAGES:
        folder = args.output / lang
        assets = folder / "assets"
        assets.mkdir(parents=True)
        if args.image:
            shutil.copy2(args.image, assets / image_name)
        shutil.copy2(ROOT / "assets" / "logo.png", assets / "logo.png")
        shutil.copy2(ROOT / "assets" / "instagram-white.png", assets / "instagram-white.png")
        shutil.copy2(ROOT / "assets" / "store-badges.svg", assets / "store-badges.svg")
        (folder / "index.html").write_text(render(lang, data, image_name), encoding="utf-8")
        zip_path = args.output / f"utv-hott-news-{lang}.zip"
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
            files = ["index.html", "assets/logo.png", "assets/instagram-white.png", "assets/store-badges.svg"]
            if image_name:
                files.append(f"assets/{image_name}")
            for relative in files:
                archive.write(folder / relative, relative)
        print(f"{LANGUAGES[lang]}: {zip_path}")


if __name__ == "__main__":
    main()
