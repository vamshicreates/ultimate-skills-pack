#!/usr/bin/env python3
"""Validate and render an editable preliminary film budget JSON as a PDF."""

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def money(value, currency):
    symbol = {"INR": "Rs ", "USD": "$", "EUR": "EUR "}.get(currency, currency + " ")
    return symbol + f"{value:,.0f}"


def validate(data):
    required = ("title", "source_file", "source_sha256", "currency", "region")
    project = data.get("project", {})
    for key in required:
        if not project.get(key):
            raise ValueError(f"Missing project.{key}")
    source = Path(project["source_file"])
    if not source.is_file():
        raise ValueError(f"Source file missing: {source}")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != project["source_sha256"]:
        raise ValueError("Source SHA-256 mismatch; analyze the current script revision first")
    if not data.get("line_items"):
        raise ValueError("At least one line item is required")
    ids = [e.get("id") for e in data.get("evidence", [])]
    if len(ids) != len(set(ids)) or any(not x for x in ids):
        raise ValueError("Evidence IDs must be present and unique")
    for index, row in enumerate(data["line_items"], 1):
        for key in ("department", "item", "unit", "basis", "evidence"):
            if not row.get(key):
                raise ValueError(f"Line {index}: missing {key}")
        for key in ("quantity", "rate"):
            if not isinstance(row.get(key), (int, float)) or row[key] < 0:
                raise ValueError(f"Line {index}: {key} must be nonnegative")
        low = row.get("low_factor", 0.8)
        high = row.get("high_factor", 1.25)
        if not 0 <= low <= 1 <= high:
            raise ValueError(f"Line {index}: require 0 <= low_factor <= 1 <= high_factor")
    contingency = data.get("contingency_rate", 0)
    if not isinstance(contingency, (int, float)) or not 0 <= contingency <= 1:
        raise ValueError("contingency_rate must be between 0 and 1")
    for index, row in enumerate(data.get("opportunities", []), 1):
        if row.get("saving_low", 0) < 0 or row.get("saving_high", 0) < row.get("saving_low", 0):
            raise ValueError(f"Opportunity {index}: invalid saving range")


def totals(data):
    departments = defaultdict(lambda: [0.0, 0.0, 0.0])
    for row in data["line_items"]:
        base = row["quantity"] * row["rate"]
        values = (base * row.get("low_factor", 0.8), base, base * row.get("high_factor", 1.25))
        for index, value in enumerate(values):
            departments[row["department"]][index] += value
    direct = [sum(values[i] for values in departments.values()) for i in range(3)]
    contingency = [amount * data.get("contingency_rate", 0) for amount in direct]
    grand = [direct[i] + contingency[i] for i in range(3)]
    return departments, direct, contingency, grand


def render(data, output):
    validate(data)
    departments, direct, contingency, grand = totals(data)
    project = data["project"]
    currency = project["currency"]
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="KickerX", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#46687a"), spaceAfter=4))
    styles.add(ParagraphStyle(name="TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.HexColor("#142a35"), spaceAfter=12))
    styles.add(ParagraphStyle(name="HeadingX", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#142a35"), spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="BudgetHeadingX", parent=styles["HeadingX"], keepWithNext=True))
    styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontSize=8.6, leading=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="SmallX", parent=styles["BodyText"], fontSize=7.3, leading=10, spaceAfter=4))
    styles.add(ParagraphStyle(name="TinyX", parent=styles["BodyText"], fontSize=6.8, leading=9))
    styles.add(ParagraphStyle(name="RightX", parent=styles["SmallX"], alignment=TA_RIGHT))
    P = lambda value, style="BodyX": Paragraph(escape(str(value)).replace("\n", "<br/>"), styles[style])

    def table(rows, widths, header=True):
        result = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
        commands = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LINEBELOW", (0, -1), (-1, -1), 0.4, colors.HexColor("#cad5da"))]
        if header:
            commands += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f0f2")), ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#8ea7b2"))]
        result.setStyle(TableStyle(commands))
        return result

    story = [P("PRELIMINARY PRODUCTION ESTIMATE", "KickerX"), P(project["title"], "TitleX")]
    story += [P(f"Script: {Path(project['source_file']).name} | Revision: {project.get('revision', 'not stated')} | Report: {project.get('report_date', date.today().isoformat())} | Region: {project['region']}", "SmallX")]
    story += [P(data.get("scope", {}).get("summary", "Script-based preliminary budget. Rates require producer and vendor confirmation."))]
    story += [P("Planning range", "HeadingX")]
    summary_rows = [[P("Low", "SmallX"), P("Base", "SmallX"), P("High", "SmallX")], [P(money(grand[0], currency), "HeadingX"), P(money(grand[1], currency), "HeadingX"), P(money(grand[2], currency), "HeadingX")]]
    story += [table(summary_rows, [56*mm, 56*mm, 56*mm]), Spacer(1, 5*mm)]
    story += [P("Range reflects explicit line-item factors and the same contingency rate in each case. These are planning allowances, not vendor quotations. No proposed saving has been deducted.", "SmallX")]

    story += [P("Script inventory", "HeadingX")]
    inventory = [[P("Measure", "SmallX"), P("Count", "SmallX"), P("Meaning", "SmallX")]]
    inventory += [[P(row.get("label", ""), "SmallX"), P(row.get("value", ""), "SmallX"), P(row.get("definition", ""), "SmallX")] for row in data.get("inventory", [])]
    story.append(table(inventory, [42*mm, 22*mm, 104*mm]))
    scope = data.get("scope", {})
    for heading, key in (("Schedule basis", "schedule"), ("Extraction and review", "quality")):
        story += [P(heading, "HeadingX"), P(scope.get(key, "Not supplied."))]

    story += [P("Budget by department", "BudgetHeadingX")]
    department_rows = [[P("Department", "SmallX"), P("Low", "RightX"), P("Base", "RightX"), P("High", "RightX")]]
    for department, values in departments.items():
        department_rows.append([P(department, "SmallX"), *[P(money(value, currency), "RightX") for value in values]])
    for label, values in (("Direct subtotal", direct), (f"Contingency ({data.get('contingency_rate', 0)*100:.0f}%)", contingency), ("TOTAL", grand)):
        department_rows.append([P(label, "SmallX"), *[P(money(value, currency), "RightX") for value in values]])
    story.append(table(department_rows, [58*mm, 36*mm, 36*mm, 38*mm]))

    story += [P("Cost drivers and assumptions", "HeadingX")]
    line_rows = [[P("Department / item", "SmallX"), P("Quantity and rate", "SmallX"), P("Base", "RightX"), P("Basis / evidence", "SmallX")]]
    for row in data["line_items"]:
        line_rows.append([P(f"{row['department']} / {row['item']}", "TinyX"), P(f"{row['quantity']:g} {row['unit']} x {money(row['rate'], currency)}", "TinyX"), P(money(row["quantity"]*row["rate"], currency), "RightX"), P(f"{row['basis']} | {row['evidence']}", "TinyX")])
    story.append(table(line_rows, [46*mm, 40*mm, 29*mm, 53*mm]))

    if data.get("evidence"):
        story += [P("Script evidence", "HeadingX")]
        evidence_rows = [[P("ID / pages", "SmallX"), P("Finding", "SmallX"), P("Budget implication", "SmallX")]]
        for e in data["evidence"]:
            evidence_rows.append([P(f"{e['id']} | p. {e.get('pages', '?')} | scenes {e.get('scenes', '?')}", "TinyX"), P(e.get("finding", ""), "TinyX"), P(e.get("cost_effect", ""), "TinyX")])
        story.append(table(evidence_rows, [43*mm, 65*mm, 60*mm]))

    if data.get("opportunities"):
        story += [P("Possible production savings", "HeadingX")]
        opportunity_rows = [[P("Option and script basis", "SmallX"), P("Likely effect / condition", "SmallX"), P("Potential range", "RightX")]]
        for row in data["opportunities"]:
            savings = f"{money(row.get('saving_low', 0), currency)} to {money(row.get('saving_high', 0), currency)}"
            opportunity_rows.append([P(f"{row.get('idea', '')} | {row.get('basis', '')}", "TinyX"), P(f"{row.get('effect', '')} {row.get('condition', '')}", "TinyX"), P(savings, "RightX")])
        story.append(table(opportunity_rows, [64*mm, 69*mm, 35*mm]))
        story.append(P("Savings overlap and are not additive until a revised schedule and vendor quotes confirm them.", "SmallX"))

    for heading, entries in (("Inclusions", scope.get("inclusions", [])), ("Exclusions", scope.get("exclusions", [])), ("Open risks and decisions", data.get("risks", []))):
        story.append(P(heading, "HeadingX"))
        story += [P(f"- {item}", "SmallX") for item in entries] or [P("None stated.", "SmallX")]
    if data.get("sources"):
        story.append(P("External references", "HeadingX"))
        for item in data["sources"]:
            story.append(P(f"{item.get('label', '')}: {item.get('url', '')} — {item.get('note', '')}", "SmallX"))
    story.append(P(f"Source SHA-256: {project['source_sha256']}", "TinyX"))

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=19*mm, bottomMargin=17*mm, title=f"{project['title']} - Preliminary Production Budget")

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#b7c8ce"))
        canvas.line(20*mm, 14*mm, 190*mm, 14*mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#5d737e"))
        canvas.drawString(20*mm, 10*mm, "PRELIMINARY | Producer planning only")
        canvas.drawRightString(190*mm, 10*mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(json.dumps({"pdf": str(output.resolve()), "low": round(grand[0]), "base": round(grand[1]), "high": round(grand[2]), "currency": currency}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_pdf", type=Path)
    args = parser.parse_args()
    render(json.loads(args.input_json.read_text()), args.output_pdf)


if __name__ == "__main__":
    main()
