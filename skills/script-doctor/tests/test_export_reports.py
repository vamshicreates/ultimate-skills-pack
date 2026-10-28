"""Real local PDF export tests, also run on Windows and macOS in CI."""

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from export_reports import export_reports, make_html, output_name, prepare_reports


REPORT = """# Synthetic coverage: The Last Call

## Overall summary
This is a synthetic report for testing the exporter, not an evaluation of a real screenplay.
The character decision has promise, but its emotional preparation needs work. Score: 70/100.

## What was analyzed
Fictional Draft 2, scenes 1-12. Complete reading in this fixture only.

## Scorecard
| Category | Score | Evidence |
| --- | --- | --- |
| Character | 7/10 | Scene 3 establishes the refusal. |
| Emotion | 7/10 | Scene 12 revisits the missed call. |

## Analysis and source locations
At script page 8, scene 3, the daughter declines a call. Scene 12 pays it off.
The café conversation is specific; her motivation is less clear. A quiet reading is plausible.

## Areas of improvement
1. Establish the personal cost before the final choice, in scene 3.
2. Preserve the restraint of scene 12. Test whether a reader understands her regret.

## Final note
REPORT_END_MARKER
"""


class ExportReportTests(unittest.TestCase):
    def test_portable_names_include_windows_reserved_and_non_latin_titles(self):
        self.assertEqual(output_name(Path("CON.md")), "report-con.pdf")
        self.assertEqual(output_name(Path("Scene 01: Revised?.md")), "report-scene-01-revised.pdf")
        name = output_name(Path("నిశ్శబ్దం.md"))
        self.assertTrue(name.isascii())
        self.assertEqual(name, output_name(Path("నిశ్శబ్దం.md")))

    def test_markdown_keeps_unicode_but_cannot_execute_html_or_fetch_images(self):
        document = make_html('# తెలుగు\n\n<script>alert(1)</script>\n\n![cover](https://example.com/pixel)', 'A <title>')
        self.assertIn("తెలుగు", document)
        self.assertIn("&lt;script&gt;", document)
        self.assertNotIn("<script>", document)
        self.assertNotIn("<img", document)
        self.assertIn("[Image omitted: cover]", document)
        self.assertIn("A &lt;title&gt;", document)

    def test_empty_missing_and_colliding_reports_fail_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "pdf"
            empty = folder / "empty.md"
            empty.write_text("", encoding="utf-8")
            for inputs in ([empty], [folder / "missing.md"], []):
                with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                    prepare_reports(inputs, output)
            first, second = folder / "a b.md", folder / "a-b.md"
            for path in (first, second):
                path.write_text(REPORT, encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare_reports([first, second], output)
            self.assertFalse(output.exists())

    def test_real_batch_export_preserves_content_sources_and_previous_pdfs(self):
        with tempfile.TemporaryDirectory(prefix="script doctor ") as temp:
            folder = Path(temp)
            reports = folder / "reports with spaces"
            reports.mkdir()
            first, second = reports / "script-01.md", reports / "script-02.md"
            first.write_text(REPORT, encoding="utf-8")
            second.write_text("# Limited assessment\n\n## Overall summary\n"
                              "UNREADABLE_SOURCE: No script content could be assessed.\n\n"
                              "## Areas of improvement\nProvide a readable export. No score assigned.", encoding="utf-8")
            before = {path: path.read_bytes() for path in (first, second)}
            with contextlib.redirect_stdout(io.StringIO()):
                result = export_reports([reports], folder / "local pdfs")
            self.assertEqual(len(result), 2)
            self.assertEqual(len(list((folder / "local pdfs").glob("*.pdf"))), 2)
            first_pdf = Path(result[0]["pdf"])
            text = "\n".join(page.extract_text() for page in PdfReader(first_pdf).pages)
            for marker in ("Overall summary", "What was analyzed", "70/100", "script page 8", "Areas of improvement", "REPORT_END_MARKER", "café"):
                self.assertIn(marker, text)
            second_text = "\n".join(page.extract_text() for page in PdfReader(result[1]["pdf"]).pages)
            self.assertIn("UNREADABLE_SOURCE", second_text)
            self.assertIn("No score assigned", second_text)
            old_pdf = first_pdf.read_bytes()
            with self.assertRaises(ValueError):
                export_reports([reports], folder / "local pdfs")
            self.assertEqual(first_pdf.read_bytes(), old_pdf)
            for path, content in before.items():
                self.assertEqual(path.read_bytes(), content)

    def test_long_report_has_multiple_pages_and_retains_last_table_row(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "long-report.md"
            rows = "\n".join(f"| Scene {i} | Evidence at script page {i}: a consequential choice. |" for i in range(1, 100))
            source.write_text(REPORT + "\n## Extended scene notes\n\n| Scene | Observation |\n| --- | --- |\n" + rows + "\n\nLONG_REPORT_END\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                result = export_reports([source], folder / "pdf")
            reader = PdfReader(result[0]["pdf"])
            self.assertGreater(len(reader.pages), 2)
            text = "\n".join(page.extract_text() for page in reader.pages)
            self.assertIn("Scene 99", text)
            self.assertIn("LONG_REPORT_END", text)

    def test_cli_returns_failure_for_missing_input(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "export_reports.py"
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(script), str(Path(temp) / "missing.md"),
                                     "--output-dir", str(Path(temp) / "pdf")], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((Path(temp) / "pdf").exists())


if __name__ == "__main__":
    unittest.main()
