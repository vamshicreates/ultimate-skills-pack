# Report helper input

Run `<python> scripts/build_report.py student.json --output-dir "reports"` using a Python with ReportLab. On Windows `<python>` can be `py -3` or `python`; on macOS/Linux it can be `python3`. For the shared isolated runtime and quoted path examples, read [platform-setup.md](platform-setup.md). The helper reads the adjacent official rubric; output is one private assessment PDF and a Results CSV row. It never uploads or grades. Use the PDF/CSV as inputs to the connected Google Sheets workflow and add verified Drive and detail-tab links there.

Input JSON fields:

```json
{
  "assessment_id": 2,
  "student_name": "Example Student",
  "student_number": "00123",
  "number_label": "Roll number",
  "contact_number": "",
  "submission_key": "source-id:tab-id:row:assessment:attempt",
  "source_reference": "Source workbook URL and tab/row",
  "submission_urls": ["actual verified submitted video URL"],
  "submission_pdf_urls": [],
  "assessed_at": "2026-10-27T16:00:00+05:30",
  "status": "Provisional",
  "review_method": "Describe actual tools and modalities reviewed",
  "coverage": "Describe actual timeline coverage and limitations",
  "full_visual_review": false,
  "full_audio_review": false,
  "answer_key_verified": false,
  "answer_key_reference": "",
  "overall_feedback": "Specific overall judgement based on the evidence",
  "priorities": ["Concrete improvement with reason"],
  "missing_items": ["Evidence that remains unavailable"],
  "items": [
    {
      "id": "c1",
      "label": "Creative concept and originality",
      "max_marks": 20,
      "awarded": null,
      "student_answer": "",
      "expected_answer": "",
      "evidence": "Timestamped observed evidence, or explicit access limitation",
      "strengths": "Specific demonstrated strength, if any",
      "gaps": "Missing/weak aspects or pending review",
      "rationale": "Explain the awarded marks and deduction, or why pending",
      "next_step": "Specific action the student can take"
    }
  ]
}
```

This excerpt illustrates one item, not a complete video record. For video, include all seven official items in rubric order (`c1` through `c7`), exact labels/maxima from rubric.json. For theory, include every actual question with stable question IDs and maxima from the verified key totalling 100, plus student_answer and, when disclosure is permitted, expected_answer. The actual theory key/reference is required for Completed. A complete video record requires full_visual_review and full_audio_review to reflect actual complete review; do not set these merely to pass validation.

Use numeric marks within each maximum, never numeric strings, and null for pending. Supported statuses are exactly `Completed`, `Provisional`, `Access blocked`, `Missing submission`, and `Needs clarification`. Only Completed produces a final /100 score; partial reviewed points remain explicitly non-final. There is no pass/fail or invented grade band. The helper validates arithmetic and evidence fields, not the truth of the review or the correctness of the key. If an explicit non-submission-zero policy applies, document it and write that administrative score in the results workbook with the policy citation; do not label an unwatched video Completed.

Add assessment_pdf_url and detail_sheet_url only after upload/creation if regenerating the CSV. Keep student/contact numbers as strings. All data in examples are placeholders, not assessed students.

The CSV is an intermediate record. Read its columns as text and use explicit plain-string/RAW cell writes; direct automatic CSV import can strip leading zeroes or interpret student text as formulas. Generate each student detail tab from the JSON, then add the verified PDF/detail URLs to the Results row. If the PDF renderer cannot display characters used in a student name or answer, render with an appropriate Unicode font and visually check the output before delivery.
