#!/usr/bin/env python3
"""Render assessor-authored evidence and marks. Does not grade or upload."""
import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

STATUSES = {'Completed', 'Provisional', 'Access blocked', 'Missing submission', 'Needs clarification'}


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError(f'{label} must be a number')
    try:
        result = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f'{label} is invalid') from error
    if not result.is_finite():
        raise ValueError(f'{label} must be finite')
    return result


def fmt(value):
    return format(value.normalize(), 'f') if value is not None else 'Pending'


def validate(data, rubric):
    if data.get('assessment_id') != rubric['assessment_id']:
        raise ValueError('assessment_id does not match this skill')
    if data.get('status') not in STATUSES:
        raise ValueError('Unsupported assessment status')
    for field in ['student_name', 'submission_key', 'source_reference', 'assessed_at',
                  'review_method', 'coverage', 'overall_feedback']:
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f'{field} is required text')
    datetime.fromisoformat(data['assessed_at'])
    for field in ['student_number', 'contact_number']:
        if not isinstance(data.get(field, ''), str):
            raise ValueError(f'{field} must be text to preserve identifiers')
    for field in ['priorities', 'missing_items', 'submission_urls', 'submission_pdf_urls']:
        if not isinstance(data.get(field, []), list) or any(not isinstance(x, str) for x in data.get(field, [])):
            raise ValueError(f'{field} must be a list of text values')
    items = data.get('items', [])
    if not isinstance(items, list):
        raise ValueError('items must be a list')
    if any(not isinstance(item, dict) for item in items):
        raise ValueError('Every item must be an object')
    ids = [item.get('id') for item in items]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('Every scoring item needs a unique text id')
    if rubric['criteria']:
        if ids != [item['id'] for item in rubric['criteria']]:
            raise ValueError('Include all seven video criteria in official order, even when pending')
        for item, official in zip(items, rubric['criteria']):
            if item.get('label') != official['label'] or item.get('max_marks') != official['max_marks']:
                raise ValueError(f"Official label or maximum changed for {official['id']}")
    total = Decimal(0)
    available = Decimal(0)
    all_graded = bool(items)
    for item in items:
        if not isinstance(item.get('label'), str) or not item['label'].strip():
            raise ValueError('Scoring items need a label')
        maximum = number(item.get('max_marks'), 'max_marks')
        if maximum <= 0:
            raise ValueError('Every item maximum must be positive')
        available += maximum
        awarded = item.get('awarded')
        if awarded is None:
            all_graded = False
            continue
        awarded = number(awarded, 'awarded')
        if not 0 <= awarded <= maximum:
            raise ValueError(f"Marks exceed bounds for {item['id']}")
        for field in ['evidence', 'rationale']:
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"Scored item {item['id']} needs {field}")
        if awarded < maximum and (not item.get('gaps') or not item.get('next_step')):
            raise ValueError(f"Deducted item {item['id']} needs gaps and next_step")
        total += awarded
    complete = data['status'] == 'Completed'
    if complete:
        if not all_graded or available != 100:
            raise ValueError('Completed requires all items scored with maxima totalling 100')
        if not data.get('student_number'):
            raise ValueError('Completed requires a resolved student number with its correct label')
        if rubric['assessment_id'] == 1:
            if data.get('answer_key_verified') is not True or not data.get('answer_key_reference'):
                raise ValueError('Theory completion requires a verified actual key and its reference')
        elif data.get('full_visual_review') is not True or data.get('full_audio_review') is not True:
            raise ValueError('Video completion requires actual full visual and audio review')
    return total if complete else None, total, items


def render(data, rubric, output):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

    final, observed, items = validate(data, rubric)
    output.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r'[^A-Za-z0-9_-]+', '-', data.get('student_number') or data['student_name']).strip('-')[:48] or 'student'
    digest = hashlib.sha256(data['submission_key'].encode()).hexdigest()[:10]
    stem = f"assessment-{rubric['assessment_id']}-{slug}-{digest}"
    pdf = output / f'{stem}.pdf'
    csv_path = output / f'{stem}.csv'
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SmallText', parent=styles['BodyText'], fontSize=9, leading=12, spaceAfter=5))
    styles.add(ParagraphStyle(name='CellText', parent=styles['BodyText'], fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='ScoreText', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#163A58')))
    styles.add(ParagraphStyle(name='TableHead', parent=styles['CellText'], textColor=colors.white))

    def p(value, style='SmallText'):
        return Paragraph(escape(str(value or '')).replace('\n', '<br/>'), styles[style])

    story = [p('MRU · AI IN CONTENT CREATION & CREATOR ECONOMY', 'Title'),
             p(rubric['title'], 'Heading1'), p('Individual student assessment', 'Heading2')]
    identity = [('Student', data['student_name']),
                (data.get('number_label') or 'Student number', data.get('student_number') or 'Unresolved'),
                ('Status', data['status']), ('Assessed', data['assessed_at'])]
    if data.get('contact_number'):
        identity.append(('Contact number', data['contact_number']))
    for label, value in identity:
        story.append(p(f'{label}: {value}'))
    story.append(p(f'Final score: {fmt(final)}' + (' / 100' if final is not None else ' — final score not issued'), 'ScoreText'))
    if final is None and any(item.get('awarded') is not None for item in items):
        story.append(p(f'Observed awarded points: {fmt(observed)}. Partial review only; not a final /100 score.'))
    story.extend([p('Overall evaluation', 'Heading2'), p(data['overall_feedback']),
                  p('Review evidence and coverage', 'Heading2'), p(data['review_method']), p(data['coverage']),
                  p(f"Source response: {data['source_reference']}")])
    for url in data.get('submission_urls', []):
        story.append(p(f'Submission: {url}'))
    for url in data.get('submission_pdf_urls', []):
        story.append(p(f'Submission PDF: {url}'))
    if data.get('answer_key_reference'):
        story.append(p(f"Answer key / allocation: {data['answer_key_reference']}"))
    story.extend([p('Mark breakdown', 'Heading2')])
    table_rows = [[p('Criterion / question', 'TableHead'), p('Awarded', 'TableHead'), p('Maximum', 'TableHead'), p('Deducted', 'TableHead')]]
    for item in items:
        awarded = None if item.get('awarded') is None else number(item['awarded'], 'awarded')
        maximum = number(item['max_marks'], 'max_marks')
        table_rows.append([p(item['label'], 'CellText'), p(fmt(awarded), 'CellText'),
                           p(fmt(maximum), 'CellText'), p(fmt(maximum-awarded) if awarded is not None else 'Pending', 'CellText')])
    table_rows.append([p('Final total', 'CellText'), p(fmt(final), 'CellText'), p('100', 'CellText'), p(fmt(100-final) if final is not None else 'Pending', 'CellText')])
    table = Table(table_rows, colWidths=[100*mm, 24*mm, 24*mm, 24*mm], repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,0),colors.HexColor('#163A58')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F1F5F8'),colors.white]),
        ('VALIGN',(0,0),(-1,-1),'TOP'), ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7), ('LINEBELOW',(0,-1),(-1,-1),0.8,colors.HexColor('#163A58'))]))
    story.extend([table, Spacer(1,5*mm), p('Detailed feedback', 'Heading2')])
    for item in items:
        awarded = None if item.get('awarded') is None else number(item['awarded'], 'awarded')
        story.append(KeepTogether([p(item['label'], 'Heading3'), p(f"{fmt(awarded)} / {fmt(number(item['max_marks'], 'max_marks'))}")]))
        for label, field in [('Student answer','student_answer'), ('Expected answer / concepts','expected_answer'),
                             ('Evidence','evidence'), ('Strengths','strengths'), ('Missing or weak','gaps'),
                             ('Mark rationale','rationale'), ('Action to improve','next_step')]:
            if item.get(field):
                story.append(p(f'{label}: {item[field]}'))
        if awarded is None:
            story.append(p('This item is pending; no mark has been inferred.'))
    for title, field in [('Improvement priorities','priorities'), ('Missing deliverables or evidence','missing_items')]:
        story.append(p(title, 'Heading2'))
        values = data.get(field, [])
        story.extend(p(f'{i}. {value}') for i,value in enumerate(values,1))
        if not values:
            story.append(p('None identified in this review.'))
    story.extend([Spacer(1,4*mm), p(f"Rubric source: {rubric['source_document']}, page {rubric['source_page']}. Each assessment is independently out of 100."),
                  p(f"Record key: {data['submission_key']}")])

    def footer(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#516171'))
        canvas.drawString(19*mm, 12*mm, 'Student assessment · Assessor copy')
        canvas.drawRightString(191*mm, 12*mm, f'Page {doc.page}')

    SimpleDocTemplate(str(pdf), pagesize=(210*mm,297*mm), rightMargin=19*mm, leftMargin=19*mm,
                      topMargin=17*mm, bottomMargin=20*mm).build(story, onFirstPage=footer, onLaterPages=footer)
    row = {'Student name':data['student_name'], data.get('number_label') or 'Student number':data.get('student_number',''),
           'Contact number':data.get('contact_number',''), 'Assessment':rubric['title'], 'Status':data['status'],
           'Total /100':fmt(final) if final is not None else '', 'Maximum marks':'100',
           **{item['id']+' — '+item['label']:fmt(number(item['awarded'],'awarded')) if item.get('awarded') is not None else '' for item in items},
           'Source reference':data['source_reference'], 'Submission links':'\n'.join(data.get('submission_urls',[])),
           'Submission PDF':'\n'.join(data.get('submission_pdf_urls',[])),
           'Assessment PDF':data.get('assessment_pdf_url',''), 'Student detail sheet':data.get('detail_sheet_url',''),
           'Missing items':'\n'.join(data.get('missing_items',[])), 'Improvement priorities':'\n'.join(data.get('priorities',[])),
           'Assessed at':data['assessed_at'], 'Review method':data['review_method'], 'Submission key':data['submission_key']}
    with csv_path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f,fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    return {'pdf':str(pdf.resolve()), 'csv':str(csv_path.resolve()), 'status':data['status'],
            'final_score':fmt(final) if final is not None else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_json',type=Path)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args()
    rubric_path = Path(__file__).resolve().parent.parent/'references/rubric.json'
    try:
        result = render(json.loads(args.input_json.read_text(encoding='utf-8-sig')), json.loads(rubric_path.read_text(encoding='utf-8-sig')), args.output_dir)
    except ModuleNotFoundError as error:
        if error.name and error.name.startswith('reportlab'):
            parser.exit(2, 'ReportLab is missing. Use the installed report runtime or install this skill\'s requirements.txt into a virtual environment.\n')
        raise
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(2, f'Assessment record invalid: {error}\n')
    print(json.dumps(result,ensure_ascii=True))


if __name__ == '__main__':
    main()
