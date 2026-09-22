from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from ai_tooling.cli import main
from tests.helpers import write_json, write_text


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".ai-tooling/backups" not in path.relative_to(root).as_posix()
    }


class EndToEndTests(unittest.TestCase):
    def test_init_preserves_existing_content_is_idempotent_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(
                project / "package.json",
                {
                    "name": "customer-portal",
                    "dependencies": {"react": "^18.3.0"},
                    "devDependencies": {"vite": "^5.4.0", "typescript": "^5.5.0"},
                },
            )
            write_text(project / "src" / "app.module.scss", ".app {}\n")
            write_text(project / "README.md", "# Customer Portal\n\nKeep README prose.\n")
            write_text(project / "AGENTS.md", "# Existing Instructions\n\nKeep agent prose.\n")
            write_json(project / ".cursor" / "settings.json", {"editor.tabSize": 4})

            first_output = StringIO()
            with redirect_stdout(first_output):
                first_status = main(["init", str(project)])
            first_snapshot = snapshot(project)
            second_status = main(["init", str(project)])
            second_snapshot = snapshot(project)
            verify_status = main(["verify", str(project)])

            self.assertEqual(first_status, 0)
            self.assertIn("OK: AI tooling", first_output.getvalue())
            self.assertEqual(second_status, 0)
            self.assertEqual(verify_status, 0)
            self.assertEqual(first_snapshot, second_snapshot)
            self.assertIn("Keep README prose.", (project / "README.md").read_text(encoding="utf-8"))
            self.assertIn("Keep agent prose.", (project / "AGENTS.md").read_text(encoding="utf-8"))
            self.assertEqual(
                __import__("json").loads((project / ".cursor" / "settings.json").read_text(encoding="utf-8"))[
                    "editor.tabSize"
                ],
                4,
            )
            filenames = [path.name for path in project.rglob("*")]
            self.assertFalse(any("<" in name or ">" in name for name in filenames))

    def test_generic_profile_skips_frontend_editor_and_snippet_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_text(project / "pyproject.toml", "[project]\nname = 'service'\n")

            status = main(["init", str(project), "--profile", "generic"])

            self.assertEqual(status, 0)
            self.assertFalse((project / ".cursor" / "extensions.json").exists())
            self.assertFalse((project / ".cursor" / "settings.json").exists())
            self.assertFalse((project / ".cursor" / "snippets").exists())
            self.assertTrue((project / ".cursor" / "rules" / "core-general-standards.mdc").is_file())

    def test_existing_different_cursor_source_is_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(project / "package.json", {"name": "demo", "dependencies": {"react": "18.3.0"}})
            existing_rule = project / ".cursor" / "rules" / "core-general-standards.mdc"
            write_text(existing_rule, "---\nalwaysApply: true\n---\n\n# Team-owned rule\n")

            status = main(["init", str(project)])

            self.assertEqual(status, 1)
            self.assertIn("Team-owned rule", existing_rule.read_text(encoding="utf-8"))

    def test_generated_conflict_leaves_target_completely_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(project / "package.json", {"name": "demo", "dependencies": {"react": "18.3.0"}})
            write_text(project / "README.md", "# Existing\n")
            unmanaged = project / ".codebuddy" / "rules" / "demo-project-rules.md"
            write_text(unmanaged, "# Team-owned rule\n")
            before = snapshot(project)

            status = main(["init", str(project)])

            self.assertEqual(status, 1)
            self.assertEqual(snapshot(project), before)

    def test_extra_file_in_generated_root_leaves_target_completely_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(project / "package.json", {"name": "demo", "dependencies": {"react": "18.3.0"}})
            write_text(project / "README.md", "# Existing\n")
            write_text(project / ".codebuddy" / "team-notes.md", "# Team notes\n")
            before = snapshot(project)

            status = main(["init", str(project)])

            self.assertEqual(status, 1)
            self.assertEqual(snapshot(project), before)


if __name__ == "__main__":
    unittest.main()
