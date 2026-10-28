"""Behavioral checks for the Python/browser timing handoff."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("project", ROOT / "scripts/project.py")
project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "assets/example-project.json").read_text())

    def test_example_and_media_readiness_are_distinct(self):
        self.assertEqual(project.validate(self.data, ROOT)[0], [])
        self.assertTrue(project.validate(self.data, ROOT, require_media=True)[0])

    def test_gap_and_duplicate_ids_rejected_but_transition_overlap_allowed(self):
        bad = copy.deepcopy(self.data)
        bad["shots"][1]["start"] = 5
        self.assertTrue(project.validate(bad, ROOT)[0])
        bad["shots"][1]["start"] = 4.6
        self.assertEqual(project.validate(bad, ROOT)[0], [])
        bad["shots"][1]["id"] = "reach"
        self.assertTrue(project.validate(bad, ROOT)[0])

    def test_nonfinite_and_out_of_range_times_rejected(self):
        for bad_time in (float("nan"), float("inf"), -1, 12):
            bad = copy.deepcopy(self.data)
            bad["beats"] = [bad_time]
            self.assertTrue(project.validate(bad, ROOT)[0])

    def test_unknown_lyrics_remain_unknown_through_export(self):
        self.data["lyric_mode"] = "selected"
        self.data["lyrics"] = [{"start": 1, "end": 2, "text": 'తెలుగు </script> "quoted"', "verified": False}]
        errors, warnings = project.validate(self.data, ROOT)
        self.assertEqual(errors, [])
        self.assertTrue(any("unverified" in w for w in warnings))
        output = project.export(self.data)
        payload = json.loads(output.split("window.CVM = ", 1)[1].split(";\nwindow.MUSIC", 1)[0])
        self.assertEqual(payload["lyrics"], self.data["lyrics"])
        music = json.loads(output.split("window.MUSIC = ", 1)[1].removesuffix(";\n"))
        self.assertEqual(music["sections"][0]["t1"], 12)
        self.assertEqual(music["beats"], self.data["beats"])

    def test_relative_media_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "media").mkdir()
            (base / "media/example.wav").touch()
            self.assertEqual(project.validate(self.data, base, require_media=True)[0], [])


if __name__ == "__main__":
    unittest.main()
