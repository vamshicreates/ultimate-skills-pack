#!/usr/bin/env python3
"""Save one local PDF per Markdown coverage report on Windows or macOS."""

import argparse
import base64
import hashlib
import html
import io
import json
import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def output_name(source):
    """Use portable filenames, including for non-Latin and Windows-reserved names."""
    stem = source.stem
    slug = re.sub(r"[^a-z0-9_-]+", "-", stem.lower()).strip("-_")[:64]
    if not slug:
        slug = hashlib.sha256(stem.encode("utf-8")).hexdigest()[:12]
    return f"report-{slug}.pdf"


def prepare_reports(inputs, output_dir, overwrite=False):
    sources = []
    for value in inputs:
        path = Path(value).expanduser().resolve()
        if path.is_dir():
            sources.extend(sorted(p for p in path.iterdir() if p.suffix.lower() == ".md" and p.is_file()))
        else:
            sources.append(path)
    if not sources:
        raise ValueError("No Markdown reports found. Supply report files or a dedicated reports folder.")
    destination = Path(output_dir).expanduser().resolve()
    seen_sources, seen_names, prepared = set(), set(), []
    for source in sources:
        if source.suffix.lower() != ".md" or not source.is_file():
            raise ValueError(f"Expected a Markdown report file: {source}")
        if source in seen_sources:
            raise ValueError(f"Duplicate input report: {source}")
        seen_sources.add(source)
        target = destination / output_name(source)
        if target.name.casefold() in seen_names:
            raise ValueError("Report filenames collide after Windows-safe normalization; "
                             f"give each source report a unique script ID: {source}")
        seen_names.add(target.name.casefold())
        if target.exists() and not overwrite:
            raise ValueError(f"PDF already exists: {target}. Use a new run folder or --overwrite.")
        if target.is_symlink():
            raise ValueError(f"Refusing to replace a linked output: {target}")
        text = source.read_text(encoding="utf-8-sig")
        if not text.strip():
            raise ValueError(f"Report is empty: {source}")
        if target.resolve() == source:
            raise ValueError("Report source and PDF destination must be different files")
        prepared.append((source, target, text))
    return prepared


def make_html(markdown, title, fonts=(), language="en"):
    from markdown_it import MarkdownIt

    if not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", language):
        raise ValueError("Use a language tag such as en, te, hi, or en-IN")
    renderer = MarkdownIt("commonmark", {"html": False}).enable("table")
    # Coverage is text. Do not fetch remote or local images referenced in Markdown.
    def image_as_text(tokens, index, options, env):
        return html.escape("[Image omitted: " + tokens[index].content + "]")
    renderer.renderer.rules["image"] = image_as_text
    body = renderer.render(markdown)
    faces, families = [], []
    for index, value in enumerate(fonts):
        font = Path(value).expanduser().resolve()
        formats = {".ttf": ("font/ttf", "truetype"), ".otf": ("font/otf", "opentype"),
                   ".woff": ("font/woff", "woff"), ".woff2": ("font/woff2", "woff2")}
        if font.suffix.lower() not in formats:
            raise ValueError(f"Unsupported font format: {font}; use TTF, OTF, WOFF, or WOFF2")
        mime, format_name = formats[font.suffix.lower()]
        encoded = base64.b64encode(font.read_bytes()).decode("ascii")
        family = f"ReportFont{index}"
        faces.append(f"@font-face {{font-family:'{family}';src:url(data:{mime};base64,{encoded}) "
                     f"format('{format_name}');font-style:normal;font-weight:100 900;}}")
        families.append(f"'{family}', ")
    css = (SKILL_ROOT / "assets" / "report.css").read_text(encoding="utf-8")
    css = "\n".join(faces) + "\n" + css.replace("REPORT_FONTS ", "".join(families))
    return f"""<!doctype html>
<html lang="{language}"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; font-src data:;">
<title>{html.escape(title)}</title><style>{css}</style></head>
<body><div class="eyebrow">SCRIPT DOCTOR / COVERAGE</div><main dir="auto">{body}</main></body></html>"""


def export_reports(inputs, output_dir, fonts=(), language="en", overwrite=False):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader

    prepared = prepare_reports(inputs, output_dir, overwrite)
    # Preflight all input text/fonts before generating the first PDF.
    documents = [(source, target, make_html(text, source.stem, fonts, language))
                 for source, target, text in prepared]
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(java_script_enabled=False, service_workers="block")
            context.route("**/*", lambda route: route.abort())
            page = context.new_page()
            for source, target, document in documents:
                page.set_content(document, wait_until="load")
                page.evaluate("document.fonts.ready")
                pdf = page.pdf(
                    format="A4", print_background=True, prefer_css_page_size=True, tagged=True,
                    display_header_footer=True, header_template="<span></span>",
                    footer_template='<div style="font-family:Arial;font-size:8px;width:100%;'
                                    'text-align:center;color:#687483">Script Doctor · '
                                    '<span class="pageNumber"></span> / '
                                    '<span class="totalPages"></span></div>',
                )
                reader = PdfReader(io.BytesIO(pdf))
                if not pdf.startswith(b"%PDF-") or not reader.pages:
                    raise ValueError(f"Renderer did not produce a valid PDF for {source}")
                if not any((p.extract_text() or "").strip() for p in reader.pages):
                    raise ValueError(f"PDF has no extractable text: {source}; inspect fonts and source")
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("wb" if overwrite else "xb") as stream:
                    stream.write(pdf)
                results.append({"source": str(source), "pdf": str(target),
                                "pages": len(reader.pages), "bytes": target.stat().st_size})
                print(json.dumps(results[-1], ensure_ascii=True), flush=True)
        finally:
            browser.close()
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=Path, help="Markdown reports or a dedicated folder")
    parser.add_argument("--output-dir", required=True, type=Path, help="Local directory for separate PDFs")
    parser.add_argument("--font", action="append", default=[], type=Path, help="Embed a local font; repeat as needed")
    parser.add_argument("--language", default="en", help="Report language tag, e.g. en, te, hi")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly replace existing PDFs")
    args = parser.parse_args(argv)
    try:
        export_reports(args.reports, args.output_dir, args.font, args.language, args.overwrite)
        return 0
    except ImportError as error:
        print(f"Missing PDF dependency: {error}. Install requirements.txt with this Python, then run "
              "python -m playwright install chromium.", file=sys.stderr)
    except Exception as error:
        print(f"PDF export failed: {error}\nIf Chromium is missing, run this interpreter with "
              "-m playwright install chromium. Earlier successfully saved PDFs remain on disk.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
