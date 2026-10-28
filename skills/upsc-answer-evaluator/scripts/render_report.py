#!/usr/bin/env python3
"""Render reviewed evaluation JSON locally; no OCR, model inference or network access."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlparse
from xml.sax.saxutils import escape, quoteattr

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from pypdf import PdfReader

INK = colors.HexColor('#193447')
TEAL = colors.HexColor('#087F83')
MUTED = colors.HexColor('#536473')


def validate(data):
    def string(value, name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{name} must be a non-empty string')
        if not value.isascii():
            raise ValueError(f'{name}: use ASCII text or extend renderer with an embedded language font')

    for name in ('title', 'subtitle', 'review_date', 'metadata', 'question', 'verdict'):
        string(data.get(name), name)
    for name, low, high in [('strengths', 1, 3), ('feedback', 1, 4), ('priorities', 3, 3),
                            ('model_outline', 1, 5), ('notes', 1, 3), ('sources', 1, 8)]:
        if not isinstance(data.get(name), list) or not low <= len(data[name]) <= high:
            raise ValueError(f'{name} must contain {low}-{high} items')
    ids = set()
    for source in data['sources']:
        for name in ('id', 'title', 'url', 'locator', 'checked'):
            string(source.get(name), 'sources.' + name)
        parsed = urlparse(source['url'])
        if parsed.scheme not in ('https', 'http') or not parsed.netloc:
            raise ValueError('Source URL must be an absolute HTTP(S) URL')
        if source['id'] in ids:
            raise ValueError('Duplicate source ID')
        ids.add(source['id'])
    for name in ('strengths', 'priorities', 'notes'):
        for item in data[name]:
            string(item, name)
    for name, fields in [('feedback', ('location', 'student_excerpt', 'status', 'explanation', 'revision')),
                         ('model_outline', ('label', 'text'))]:
        for item in data[name]:
            for field in fields:
                string(item.get(field), name + '.' + field)
            refs = item.get('source_ids')
            if not isinstance(refs, list) or any(not isinstance(x, str) or x not in ids for x in refs):
                raise ValueError(f'{name}: unresolved source reference')
    return data


def render(data, destination):
    validate(data)
    styles = {
        'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=23, leading=27, textColor=INK, spaceAfter=7),
        'sub': ParagraphStyle('sub', fontName='Helvetica', fontSize=10, leading=14, textColor=MUTED, spaceAfter=8),
        'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=TEAL, spaceBefore=9, spaceAfter=5),
        'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=14, textColor=INK, spaceAfter=5, alignment=TA_LEFT),
        'small': ParagraphStyle('small', fontName='Helvetica', fontSize=8.4, leading=11.5, textColor=MUTED, spaceAfter=4),
    }
    def para(text, style='body'):
        return Paragraph(escape(text), styles[style])
    def labelled(label, text, style='body'):
        return Paragraph('<b>' + escape(label) + '</b> ' + escape(text), styles[style])
    def refs(item):
        return (' [' + ', '.join(item['source_ids']) + ']') if item['source_ids'] else ''
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#D7E3E7'))
        canvas.line(42, 39, A4[0] - 42, 39)
        canvas.setFillColor(MUTED)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(42, 26, 'UPSC ANSWER REVIEW  |  ' + data['review_date'])
        canvas.drawRightString(A4[0] - 42, 26, f'{doc.page} / 2')
        canvas.restoreState()

    story = [para(data['title'], 'title'), para(data['subtitle'], 'sub'), para(data['metadata'], 'small'),
             labelled('Question', data['question'], 'small'), para('Assessment', 'h2'), para(data['verdict']),
             para('What works', 'h2')]
    story += [labelled('+', item) for item in data['strengths']]
    story.append(para('What to improve', 'h2'))
    for i, item in enumerate(data['feedback'], 1):
        story.append(KeepTogether([
            labelled(f'{i:02d}  {item["status"].upper()}', item['location'], 'small'),
            labelled('You wrote:', '"' + item['student_excerpt'] + '"'),
            para(item['explanation'] + refs(item)),
            labelled('Improve:', item['revision']), Spacer(1, 5)
        ]))
    story.extend([PageBreak(), para('Your next attempt', 'title'), para('Three priorities, then a stronger answer outline.', 'sub')])
    for i, item in enumerate(data['priorities'], 1):
        story.append(labelled(f'{i}.', item))
    story.append(para('Model-answer outline', 'h2'))
    story.append(para('Illustrative structure, not an official UPSC answer. Adapt to the prescribed word limit.', 'small'))
    for item in data['model_outline']:
        story.append(labelled(item['label'], item['text'] + refs(item)))
    story.append(para('Reading and verification notes', 'h2'))
    story += [para(item, 'small') for item in data['notes']]
    story.append(para('Sources checked', 'h2'))
    for source in data['sources']:
        label = f'[{source["id"]}] {source["title"]}'
        story.append(Paragraph(f'<link href={quoteattr(source["url"])} color="#087F83">{escape(label)}</link>'
                               + escape(' - ' + source['locator']), styles['small']))

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix='.pdf', dir=destination.parent)
    os.close(fd)
    try:
        doc = SimpleDocTemplate(tmp, pagesize=A4, rightMargin=42, leftMargin=42,
                                topMargin=38, bottomMargin=51, title=data['title'], author='UPSC Answer Evaluator')
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        reader = PdfReader(tmp)
        if len(reader.pages) != 2:
            raise ValueError(f'Report has {len(reader.pages)} pages; shorten copy to fit two pages. Output not replaced.')
        if any(not page.extract_text().strip() for page in reader.pages):
            raise ValueError('Empty PDF page')
        os.replace(tmp, destination)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evaluation', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        result = render(json.loads(args.evaluation.read_text(encoding='utf-8')), args.output)
    except (ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f'Cannot render report: {exc}\n')
    print(result.resolve())
