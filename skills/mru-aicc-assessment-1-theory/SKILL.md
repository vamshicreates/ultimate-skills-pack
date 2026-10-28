---
name: mru-aicc-assessment-1-theory
description: Assess MRU AICC Week 3 theory questionnaire responses using the actual Google Form answer key and question marks; produce individual feedback PDFs and a separate Google Sheets results workbook.
---

# Assessment 1 — Theory Knowledge

Assess each selected student's submission, explain earned and lost marks, create a detailed individual assessment PDF and detail tab, and record their name, number, score, and PDF link in a new Google Sheets results workbook.

## Load the assessment

Read [references/rubric.json](references/rubric.json), [references/assessment-guide.md](references/assessment-guide.md), and [references/workflow.md](references/workflow.md) before grading. The official source is bundled at [references/framework.pdf](references/framework.pdf), page 1. Preserve its criteria and maxima. Assessment 1 is independently out of 100.

This is a questionnaire assessment. Obtain the actual Form answer key and question mark allocation; the framework does not provide them. Score all questions using those settings and explain every missed concept. A missing key prevents a final score. Video review is not required unless the actual questionnaire requires it.

## Produce and deliver

Use the response sheet as the source and create a separate results workbook. Preserve source rows and submission links. Give every selected student a visible status, including inaccessible/missing submissions. Create one detail tab and one PDF per student. Put the verified individual PDF link in the same Results row as the student's name, correctly labelled number, and score. Preserve any original submission PDF as a separately labelled link.

For deterministic PDF generation and score validation, read [references/report-input.md](references/report-input.md), then run `scripts/build_report.py` on the evidence and awarded marks. The script performs no video review, grading judgement, uploads, or live sheet edits. Use connected Google Drive/Sheets tools for delivery, with the available Google Sheets skill when applicable. Verify uploads, row identities, component sums and links before reporting completion.

For a request only to explain the rubric or prepare an assessment template, provide that deliverable without starting cohort grading. For a live assessment request, resolve the source response sheet from supplied context or connected sources and continue through the complete requested cohort. Ask only for consequential missing inputs that cannot be resolved.

## Platform setup

For Windows, macOS, Linux, missing dependencies or interpreter selection, read [references/platform-setup.md](references/platform-setup.md). Use the current computer's paths and available Python runtime.
