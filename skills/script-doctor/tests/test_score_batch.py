"""Behavioral checks for ranking, comparability, and incomplete evidence handling."""

import copy
import csv
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from score_batch import RUBRIC_ID, WEIGHTS, evaluate, render_csv


def entry(script_id="a", score=7):
    return {
        "id": script_id, "title": "నిశ్శబ్దం", "source": f"{script_id}.fountain",
        "draft": "Draft 1", "role": "candidate", "language": "Telugu",
        "genre": "Drama", "rubric_id": RUBRIC_ID, "read_status": "complete",
        "confidence": "high", "limitations": [],
        "scores": {key: score for key in WEIGHTS},
    }


def batch(*entries):
    return {"rubric_id": RUBRIC_ID, "weights": dict(WEIGHTS), "scripts": list(entries)}


class ScoreBatchTests(unittest.TestCase):
    def test_format_groups_have_independent_ranks_and_close_calls(self):
        micro_a, micro_b, feature = entry("micro-a", 7), entry("micro-b", 7), entry("feature", 7)
        for row in (micro_a, micro_b):
            row.update(format="micro_drama", evaluation_unit="standalone", runtime_minutes=2,
                       runtime_basis="user_stated", comparison_group="two-minute-standalone")
        feature.update(format="feature", evaluation_unit="standalone", runtime_minutes=120,
                       runtime_basis="user_stated")
        result = evaluate(batch(micro_a, feature, micro_b))
        rows = {row["id"]: row for row in result["scripts"]}
        self.assertEqual([rows[key]["total"] for key in rows], [70, 70, 70])
        self.assertEqual(rows["feature"]["rank"], 1)
        self.assertEqual(rows["feature"]["close_to"], [])
        self.assertEqual(rows["micro-a"]["close_to"], ["micro-b"])
        self.assertEqual(rows["micro-b"]["rank"], 1)
        self.assertEqual(result["ranking_scope"], "within comparison_group")
        self.assertEqual(len(result["groups"]), 2)

    def test_explicit_shared_group_allows_requested_overall_comparison(self):
        micro, feature = entry("micro", 8), entry("feature", 7)
        micro.update(format="micro_drama", evaluation_unit="standalone")
        feature.update(format="feature", evaluation_unit="standalone")
        for row in (micro, feature):
            row["comparison_group"] = "requested-overall"
        result = evaluate(batch(feature, micro))
        self.assertEqual([(row["id"], row["rank"]) for row in result["scripts"]],
                         [("micro", 1), ("feature", 2)])

    def test_complete_episode_can_score_while_incomplete_season_cannot(self):
        episode, season = entry("ep-01"), entry("season-01")
        episode.update(format="web_series", evaluation_unit="episode", series_id="series-1", episode_id="S01E01")
        season.update(format="web_series", evaluation_unit="season", read_status="partial",
                      limitations=["Only the first episode of six was supplied."])
        rows = {row["id"]: row for row in evaluate(batch(episode, season))["scripts"]}
        self.assertEqual(rows["ep-01"]["total"], 70)
        self.assertEqual(rows["ep-01"]["rank"], 1)
        self.assertIsNone(rows["season-01"]["total"])
        self.assertIsNone(rows["season-01"]["rank"])

    def test_reading_a_complete_excerpt_does_not_make_it_a_complete_script(self):
        for unit in ("excerpt", "treatment"):
            row = entry()
            row.update(evaluation_unit=unit, limitations=["Only this limited dramatic scope was supplied."])
            result = evaluate(batch(row))["scripts"][0]
            self.assertIsNone(result["total"])
            self.assertIsNone(result["rank"])

    def test_invalid_runtime_and_context_are_rejected(self):
        changes = [
            {"runtime_minutes": 0, "runtime_basis": "user_stated"},
            {"runtime_minutes": -1, "runtime_basis": "user_stated"},
            {"runtime_minutes": True, "runtime_basis": "estimated"},
            {"runtime_minutes": float("inf"), "runtime_basis": "estimated"},
            {"runtime_minutes": 2}, {"runtime_basis": "timed_read"},
            {"format": "unknown-value"}, {"evaluation_unit": "unknown-value"},
            {"comparison_group": ""}, {"episode_id": ""},
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                row = entry()
                row.update(change)
                evaluate(batch(row))

    def test_csv_keeps_runtime_scope_and_series_identity(self):
        row = entry()
        row.update(format="micro_drama", evaluation_unit="episode", runtime_minutes=2,
                   runtime_basis="estimated", series_id="series-one", episode_id="ep-one",
                   comparison_group="micro-episodes")
        result = next(csv.DictReader(io.StringIO(render_csv(evaluate(batch(row))))))
        for key in ("format", "evaluation_unit", "runtime_basis", "series_id", "episode_id", "comparison_group"):
            self.assertEqual(result[key], row[key])
        self.assertEqual(result["runtime_minutes"], "2")

    def test_unicode_stdout_is_valid_json_under_legacy_console_encoding(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "score_batch.py"
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.json"
            source.write_text(json.dumps(batch(entry())), encoding="utf-8")
            env = dict(os.environ, PYTHONIOENCODING="ascii")
            result = subprocess.run([sys.executable, str(script), str(source)],
                                    env=env, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["scripts"][0]["title"], "నిశ్శబ్దం")

    def test_weighted_total_rounds_only_once_half_up(self):
        row = entry(score=7)
        row["scores"]["specificity"] = 8
        self.assertEqual(evaluate(batch(row))["scripts"][0]["total"], 71)

    def test_ties_share_rank_and_close_calls_do_not_force_ties(self):
        third = entry("c")
        third["scores"]["emotion"] = 7.5
        result = evaluate(batch(entry("b"), third, entry("a")))
        self.assertEqual([(r["id"], r["rank"]) for r in result["scripts"]],
                         [("c", 1), ("a", 2), ("b", 2)])
        self.assertEqual(result["scripts"][0]["close_to"], ["a", "b"])

    def test_missing_partial_low_confidence_and_unreadable_are_not_ranked(self):
        for issue in ("missing", "partial", "low", "unreadable"):
            with self.subTest(issue=issue):
                row = entry()
                row["limitations"] = ["Specific assessment limitation"]
                if issue == "missing":
                    row["scores"]["dialogue"] = None
                elif issue == "low":
                    row["confidence"] = "low"
                else:
                    row["read_status"] = issue
                result = evaluate(batch(row))["scripts"][0]
                self.assertIsNone(result["total"])
                self.assertIsNone(result["rank"])
                self.assertTrue(result["unranked_reasons"])

    def test_uncertainty_requires_explanation(self):
        row = entry()
        row["confidence"] = "low"
        with self.assertRaises(ValueError):
            evaluate(batch(row))

    def test_reference_cannot_win_candidate_ranking(self):
        reference = entry("reference", 10)
        reference["role"] = "reference"
        result = evaluate(batch(reference, entry()))
        self.assertEqual(result["scripts"][0]["id"], "a")
        self.assertEqual(result["scripts"][1]["total"], 100)
        self.assertIsNone(result["scripts"][1]["rank"])

    def test_invalid_numeric_scores_fail(self):
        for invalid in (True, "7", -1, 11, 7.2, float("nan"), float("inf")):
            with self.subTest(value=invalid):
                row = entry()
                row["scores"]["emotion"] = invalid
                with self.assertRaises(ValueError):
                    evaluate(batch(row))

    def test_incompatible_rubrics_and_bad_weights_fail(self):
        original = batch(entry())
        bad = []
        changed = copy.deepcopy(original)
        changed["scripts"][0]["rubric_id"] = "other"
        bad.append(changed)
        changed = copy.deepcopy(original)
        changed["weights"]["emotion"] = 21
        bad.append(changed)
        changed = copy.deepcopy(original)
        changed["weights"]["emotion"] = 21
        changed["weights"]["plot"] = 14
        bad.append(changed)
        changed = copy.deepcopy(original)
        changed["scripts"][0]["weights"] = WEIGHTS
        bad.append(changed)
        for data in bad:
            with self.subTest(data=data), self.assertRaises(ValueError):
                evaluate(data)

    def test_explicit_zero_weight_category_can_be_unassessed(self):
        data = batch(entry())
        data["rubric_id"] = data["scripts"][0]["rubric_id"] = "custom-v1"
        data["weights"]["dialogue"] = 0
        data["weights"]["cinematic"] = 20
        data["scripts"][0]["scores"]["dialogue"] = None
        self.assertEqual(evaluate(data)["scripts"][0]["total"], 70)

    def test_duplicate_ids_and_empty_batches_fail(self):
        for data in (batch(entry(), entry()), batch()):
            with self.assertRaises(ValueError):
                evaluate(data)

    def test_twenty_candidates_are_all_accounted_for(self):
        result = evaluate(batch(*(entry(f"script-{i:02}", (i % 10) + 0.5) for i in range(20))))
        self.assertEqual(result["ranked_count"], 20)
        self.assertEqual(len({row["id"] for row in result["scripts"]}), 20)
        self.assertEqual(result["scripts"][0]["total"], 95)

    def test_csv_retains_unicode_and_neutralizes_formula_titles(self):
        suspicious = entry("b")
        suspicious["title"] = " =1+1"
        rows = list(csv.DictReader(io.StringIO(render_csv(evaluate(batch(entry(), suspicious))))))
        self.assertEqual(rows[0]["title"], "నిశ్శబ్దం")
        self.assertEqual(rows[1]["title"], "' =1+1")
        self.assertEqual(rows[0]["emotion"], "7")

    def test_cli_exports_and_preserves_existing_outputs_and_source(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "score_batch.py"
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source, output, table = (folder / name for name in ("in.json", "out.json", "out.csv"))
            source.write_text(json.dumps(batch(entry())), encoding="utf-8")
            command = [sys.executable, str(script), str(source), "--json-out", str(output),
                       "--csv-out", str(table)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            exported = json.loads(output.read_text(encoding="utf-8"))["scripts"][0]
            self.assertEqual(exported["total"], 70)
            self.assertEqual(exported["title"], "నిశ్శబ్దం")
            before = output.read_bytes()
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(output.read_bytes(), before)
            self.assertEqual(subprocess.run(command + ["--overwrite"], capture_output=True).returncode, 0)
            before_source = source.read_bytes()
            bad_command = [sys.executable, str(script), str(source), "--json-out", str(source), "--overwrite"]
            self.assertEqual(subprocess.run(bad_command, capture_output=True).returncode, 2)
            self.assertEqual(source.read_bytes(), before_source)


if __name__ == "__main__":
    unittest.main()
