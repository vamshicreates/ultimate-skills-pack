#!/usr/bin/env python3
"""Extract a PDF screenplay into a reviewable scene ledger. Detection is a first pass."""

import argparse
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from pypdf import PdfReader

HEADING = re.compile(r"^\s*((?:INT\.?/?EXT\.?|EXT\.?/?INT\.?|INT\.?|EXT\.?|I/E\.)\s+.+)$", re.I)
NUMBER = re.compile(r"\s*(\d+[A-Z]?)\s+\1\s*$", re.I)
TIME = re.compile(r"\b(NIGHT|DAY|EVENING|AFTERNOON|MORNING|DAWN|DUSK|CONTINUOUS|MOMENTS LATER|LATER|EARLY MORNING)\b", re.I)


def scene_heading(line):
    match = HEADING.match(line)
    if not match:
        return None
    raw = match.group(1).strip()
    number_match = NUMBER.search(raw)
    printed = number_match.group(1) if number_match else None
    slugline = NUMBER.sub("", raw).strip() if printed else raw
    slugline = re.sub(r"\s+", " ", slugline)
    time_matches = list(TIME.finditer(slugline))
    time_of_day = time_matches[-1].group(1).upper() if time_matches else "UNSPECIFIED"
    area = re.sub(r"^(?:INT\.?/?EXT\.?|EXT\.?/?INT\.?|INT\.?|EXT\.?|I/E\.)\s*", "", slugline, flags=re.I)
    area = re.sub(r"\s*-\s*(?:DAY|NIGHT|EVENING|AFTERNOON|MORNING|DAWN|DUSK|CONTINUOUS|MOMENTS LATER|LATER|EARLY MORNING)\b.*$", "", area, flags=re.I).strip(" -.")
    return {"printed_number": printed, "slugline": slugline, "time_of_day": time_of_day, "location_area": area}


def read_pages(source):
    extension = source.suffix.lower()
    if extension == ".pdf":
        reader = PdfReader(str(source))
        return [page.extract_text() or "" for page in reader.pages], "PDF page"
    if extension == ".docx":
        from docx import Document
        return ["\n".join(paragraph.text for paragraph in Document(str(source)).paragraphs)], "document section"
    if extension == ".fdx":
        root = ET.parse(source).getroot()
        paragraphs = []
        for paragraph in root.findall(".//Paragraph"):
            paragraphs.append("".join(paragraph.itertext()).strip())
        return ["\n".join(paragraphs)], "document section"
    if extension in (".fountain", ".txt", ".md"):
        return [source.read_text(encoding="utf-8-sig")], "document section"
    raise ValueError(f"Unsupported script format: {extension}")


def extract(source):
    contents, page_unit = read_pages(source)
    pages = []
    warnings = []
    scenes = []
    current = None
    for page_number, content in enumerate(contents, 1):
        pages.append({"page": page_number, "characters": len(content)})
        if len(content.strip()) < 40:
            warnings.append(f"{page_unit} {page_number} has little extractable text; inspect/OCR it.")
        for line in content.splitlines():
            heading = scene_heading(line)
            if heading:
                current = {"id": f"SC-{len(scenes)+1:03}", **heading, "start_source_unit": page_number, "end_source_unit": page_number, "body": ""}
                if page_unit == "PDF page":
                    current["start_pdf_page"] = page_number
                    current["end_pdf_page"] = page_number
                scenes.append(current)
            elif current is not None:
                current["body"] += line + "\n"
                current["end_source_unit"] = page_number
                if page_unit == "PDF page":
                    current["end_pdf_page"] = page_number
    ids = [s["printed_number"] for s in scenes if s["printed_number"]]
    if len(ids) != len(set(ids)):
        warnings.append("Duplicate printed scene numbers; review heading detection.")
    if not scenes:
        warnings.append("No scenes detected; inspect formatting or OCR before estimating.")
    if page_unit != "PDF page":
        warnings.append("This format has no reliable PDF page references; use scene numbers/lines and verify the original pagination.")
    return {"source_file": str(source.resolve()), "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "source_units": len(contents), "source_unit_name": page_unit, "pages": pages, "scene_count": len(scenes), "scenes": scenes, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    result = extract(args.source)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "scene-ledger.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    with (args.output_dir / "scene-ledger.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "printed_number", "slugline", "start_source_unit", "end_source_unit", "time_of_day", "location_area"])
        writer.writeheader()
        writer.writerows({key: scene.get(key) for key in writer.fieldnames} for scene in result["scenes"])
    print(json.dumps({"source": str(args.source), "source_units": result["source_units"], "unit_name": result["source_unit_name"], "scenes": result["scene_count"], "warnings": result["warnings"]}, indent=2))


if __name__ == "__main__":
    main()
