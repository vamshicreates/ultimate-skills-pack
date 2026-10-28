import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import yaml

SPEC = importlib.util.spec_from_file_location("sharing", Path(__file__).parents[1] / "scripts/skills_everywhere.py")
sharing = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sharing)


class SharingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home with spaces"
        self.home.mkdir()
        self.home = self.home.resolve()
        self.root = self.home / ".local/share/test-library"

    def skill(self, path, name="review", body="Review the change.", extra=None):
        path.mkdir(parents=True, exist_ok=True)
        meta = {"name": name, "description": "Review requested changes"}
        meta.update(extra or {})
        (path / "SKILL.md").write_text("---\n" + yaml.safe_dump(meta) + "---\n" + body)
        return path

    def library(self, **kwargs):
        return sharing.Library(self.home, self.root, **kwargs)

    def apply(self, **kwargs):
        with sharing.locked(self.root):
            return self.library(**kwargs).sync()

    def test_plan_has_no_filesystem_writes(self):
        self.skill(self.home / ".claude/skills/review")
        library = self.library()
        entries, skipped = library.scan()
        self.assertEqual(library.plan(entries, skipped)["targets"]["agents"]["add"], 1)
        self.assertFalse(self.root.exists())
        self.assertFalse((self.home / ".agents").exists())

    def test_shares_assets_preserves_original_and_is_idempotent(self):
        source = self.skill(self.home / ".claude/skills/review", extra={"disable-model-invocation": True})
        script = source / "scripts/check.sh"
        script.parent.mkdir()
        script.write_text("exit 0\n")
        original = (source / "SKILL.md").read_bytes()
        first = self.apply(all_agents=True)
        second = self.apply()
        self.assertEqual(first["entries"], second["entries"])
        self.assertTrue(all(v["add"] == 0 for v in second["targets"].values()))
        for relative in sharing.AGENTS.values():
            skill = self.home / relative / "review"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertEqual((skill / "scripts/check.sh").read_text(), "exit 0\n")
        self.assertEqual((source / "SKILL.md").read_bytes(), original)
        meta, _ = sharing.manifest(self.home / ".codex/skills/review/SKILL.md")
        self.assertTrue(meta["disable-model-invocation"])

    def test_conflicting_versions_are_available_to_both_agents(self):
        self.skill(self.home / ".claude/skills/review", body="Claude version")
        self.skill(self.home / ".codex/skills/review", body="Codex version")
        report = self.apply()
        self.assertEqual(report["definitions"], 2)
        self.assertEqual(report["entries"], 3)
        catalog = json.loads((self.root / "catalog.json").read_text())["entries"]
        variants = [e for e in catalog if e["name"] != "review"]
        self.assertEqual(len(variants), 2)
        for e in variants:
            for relative in [".claude/skills", ".codex/skills"]:
                meta, _ = sharing.manifest(self.home / relative / e["name"] / "SKILL.md")
                self.assertEqual(meta["name"], e["name"])

    def test_supporting_script_differences_are_distinct_bundles(self):
        for folder, body in [(".claude/skills/review", "exit 0"), (".codex/skills/review", "exit 1")]:
            source = self.skill(self.home / folder)
            (source / "check.sh").write_text(body)
        self.assertEqual(self.apply()["definitions"], 2)

    def test_identical_bundles_deduplicate(self):
        self.skill(self.home / ".claude/skills/review")
        self.skill(self.home / ".codex/skills/review")
        self.assertEqual(self.apply()["definitions"], 1)

    def test_invalid_yaml_and_duplicate_keys_are_skipped(self):
        bad = self.home / ".claude/skills/bad"
        bad.mkdir(parents=True)
        (bad / "SKILL.md").write_text("---\nname: bad\nname: other\ndescription: hello\n---\n")
        self.assertEqual(len(self.apply()["skipped"]), 1)
        self.assertFalse((self.home / ".agents/skills/bad").exists())

    def test_unsafe_yaml_tag_is_not_executed(self):
        bad = self.home / ".claude/skills/bad"
        bad.mkdir(parents=True)
        (bad / "SKILL.md").write_text("---\nname: bad\ndescription: !!python/object/apply:os.system ['touch /tmp/never-run-this']\n---\n")
        self.assertEqual(len(self.apply()["skipped"]), 1)

    def test_uninstall_preserves_originals_and_changed_links(self):
        source = self.skill(self.home / ".claude/skills/review")
        self.apply(all_agents=True)
        replaced = self.home / ".codex/skills/review"
        replaced.unlink()
        replacement = self.skill(self.home / "personal-review", body="My replacement")
        replaced.symlink_to(replacement)
        result = self.library().uninstall()
        self.assertIn(str(replaced), result["changed_paths_preserved"])
        self.assertTrue((source / "SKILL.md").is_file())
        self.assertEqual(replaced.resolve(), replacement)
        self.assertFalse((self.home / ".cursor/skills/review").exists())

    def test_future_skill_is_picked_up_from_inbox(self):
        self.apply(all_agents=True)
        self.skill(self.root / "inbox/next", name="next")
        self.apply()
        self.assertTrue((self.home / ".codex/skills/next/SKILL.md").is_file())

    def test_scope_is_persisted_and_existing_files_win(self):
        source = self.skill(self.home / "collection/review")
        existing = self.skill(self.home / ".codex/skills/review", body="Existing")
        original = (existing / "SKILL.md").read_text()
        report = self.apply(sources=[str(source)], agents=["codex"])
        self.assertEqual(set(report["targets"]), {"codex"})
        self.assertEqual(set(self.apply()["targets"]), {"codex"})
        self.assertEqual((existing / "SKILL.md").read_text(), original)
        self.assertFalse((self.home / ".agents/skills").exists())

    def test_following_symlink_cycles_terminates(self):
        source = self.skill(self.home / ".claude/skills/review")
        (source / "loop").symlink_to(source)
        self.assertEqual(self.apply()["definitions"], 1)

    def test_generated_file_edit_is_preserved(self):
        self.skill(self.home / ".claude/skills/review")
        self.apply()
        generated = self.root / "definitions/review/SKILL.md"
        generated.write_text("My manual edit")
        with self.assertRaisesRegex(ValueError, "preserving"):
            self.apply()
        self.assertEqual(generated.read_text(), "My manual edit")

    def test_journal_recovers_links_after_interrupted_sync(self):
        self.root.mkdir(parents=True)
        source = self.skill(self.home / "source")
        dest = self.home / ".codex/skills/review"
        dest.parent.mkdir(parents=True)
        dest.symlink_to(source)
        (self.root / "journal.jsonl").write_text(json.dumps({"path": str(dest), "target": str(source)}) + "\n")
        self.assertTrue(self.library().owned_link(dest))
        self.library().uninstall()
        self.assertFalse(dest.exists())

    def test_runtime_skill_is_discoverable_as_explicit_source(self):
        source = self.skill(self.root / "runtime/skill", name="skills-everywhere")
        self.assertEqual(self.apply(sources=[str(source)])["skill_names"], 1)

    def test_metadata_updates_on_sync(self):
        source = self.skill(self.home / ".claude/skills/review", body="First")
        self.apply()
        self.skill(source, body="Second")
        self.apply()
        self.assertIn("Second", (self.home / ".agents/skills/review/SKILL.md").read_text())

    def test_deleted_resource_does_not_leave_a_broken_registration(self):
        source = self.skill(self.home / ".claude/skills/review")
        (source / "check.sh").write_text("exit 0")
        self.apply()
        (source / "check.sh").unlink()
        self.apply()
        self.assertFalse((self.root / "definitions/review/check.sh").is_symlink())
        self.assertEqual(self.library().status()["missing_links"], [])

    def test_cli_invalid_agent_fails_without_mutating_home(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                sharing.main(["--home", str(self.home), "--agents", "unknown", "sync"])
        self.assertFalse(self.root.exists())


if __name__ == "__main__":
    unittest.main()
