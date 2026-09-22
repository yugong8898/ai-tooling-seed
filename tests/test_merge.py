from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from ai_tooling.merge import (
    END_MARKER,
    START_MARKER,
    MergeConflict,
    Operation,
    apply_operations,
    merge_json_defaults,
    merge_managed_markdown,
)


class MarkdownMergeTests(unittest.TestCase):
    def test_inserts_and_then_replaces_one_managed_block(self) -> None:
        original = "# Existing\n\nKeep this.\n"
        first = merge_managed_markdown(original, "Generated v1")
        second = merge_managed_markdown(first, "Generated v2")

        self.assertIn("Keep this.", second)
        self.assertNotIn("Generated v1", second)
        self.assertIn("Generated v2", second)
        self.assertEqual(second.count(START_MARKER), 1)
        self.assertEqual(second.count(END_MARKER), 1)

    def test_rejects_duplicate_or_unbalanced_markers(self) -> None:
        with self.assertRaises(MergeConflict):
            merge_managed_markdown(f"{START_MARKER}\na\n{START_MARKER}\nb\n{END_MARKER}", "new")
        with self.assertRaises(MergeConflict):
            merge_managed_markdown(f"{START_MARKER}\nmissing end", "new")


class JsonMergeTests(unittest.TestCase):
    def test_existing_values_win_and_missing_nested_keys_are_added(self) -> None:
        merged = merge_json_defaults(
            {"editor.tabSize": 4, "files": {"trim": True}},
            {"editor.tabSize": 2, "files": {"eol": "\n"}, "new": ["default"]},
        )

        self.assertEqual(merged["editor.tabSize"], 4)
        self.assertEqual(merged["files"], {"trim": True, "eol": "\n"})
        self.assertEqual(merged["new"], ["default"])


class ApplyOperationsTests(unittest.TestCase):
    def test_dry_run_performs_zero_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            operation = Operation(Path("README.md"), "CREATE", b"new\n", "test")

            result = apply_operations(target, [operation], dry_run=True)

            self.assertFalse((target / "README.md").exists())
            self.assertEqual(result.changed, 1)
            self.assertIsNone(result.backup_root)

    def test_update_backs_up_existing_file_before_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            readme = target / "README.md"
            readme.write_text("old\n", encoding="utf-8")
            operation = Operation(Path("README.md"), "UPDATE", b"new\n", "test")
            now = datetime(2026, 9, 22, 1, 2, 3, tzinfo=timezone.utc)

            result = apply_operations(target, [operation], dry_run=False, now=now)

            self.assertEqual(readme.read_text(encoding="utf-8"), "new\n")
            backup = target / ".ai-tooling" / "backups" / "20260922T010203Z" / "README.md"
            self.assertEqual(backup.read_text(encoding="utf-8"), "old\n")
            self.assertEqual(result.backup_root, backup.parent.resolve())

    def test_conflict_is_reported_and_never_written(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            operation = Operation(Path("unsafe.md"), "CONFLICT", None, "unmanaged file")

            result = apply_operations(target, [operation], dry_run=False)

            self.assertEqual(result.conflicts, 1)
            self.assertFalse((target / "unsafe.md").exists())

    def test_rejects_symlinked_parent_that_escapes_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside_directory:
            target = Path(directory)
            outside = Path(outside_directory)
            (target / ".cursor").symlink_to(outside, target_is_directory=True)
            operation = Operation(Path(".cursor/rules/core.mdc"), "CREATE", b"unsafe\n", "test")

            with self.assertRaises(MergeConflict):
                apply_operations(target, [operation], dry_run=False)

            self.assertFalse((outside / "rules" / "core.mdc").exists())


if __name__ == "__main__":
    unittest.main()
