from __future__ import annotations

import io
import json
import ast
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ai_tooling.cli import main
from tests.helpers import write_json


class CliTests(unittest.TestCase):
    def test_runtime_sources_parse_as_python_39(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        sources = sorted((repository / "ai_tooling").glob("*.py")) + [repository / "scripts" / "ai_tooling.py"]

        for source in sources:
            with self.subTest(source=source.name):
                ast.parse(source.read_text(encoding="utf-8"), filename=str(source), feature_version=(3, 9))

    def test_detect_prints_json_and_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(project / "package.json", {"name": "demo", "dependencies": {"react": "18.3.0"}})
            output = io.StringIO()

            with redirect_stdout(output):
                status = main(["detect", str(project)])

            self.assertEqual(status, 0)
            self.assertEqual(json.loads(output.getvalue())["projectName"], "demo")

    def test_missing_target_returns_usage_error_without_traceback(self) -> None:
        error = io.StringIO()

        with redirect_stderr(error):
            status = main(["detect", "/definitely/missing/ai-tooling-target"])

        self.assertEqual(status, 2)
        self.assertIn("ERROR", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())

    def test_init_dry_run_reports_changes_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(project / "package.json", {"name": "demo", "dependencies": {"react": "18.3.0"}})
            output = io.StringIO()

            with redirect_stdout(output):
                status = main(["init", str(project), "--dry-run"])

            self.assertEqual(status, 0)
            self.assertIn("CREATE", output.getvalue())
            self.assertFalse((project / ".cursor" / "ai-tooling.json").exists())

    def test_generate_writes_mirrors_from_cursor_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(
                project / ".cursor" / "ai-tooling.json",
                {
                    "schemaVersion": 2,
                    "projectName": "demo",
                    "profile": "frontend",
                    "enabledPolicies": [],
                    "detected": {},
                    "pendingQuestions": [],
                },
            )
            (project / ".cursor" / "rules").mkdir(parents=True)
            (project / ".cursor" / "rules" / "core-base.mdc").write_text(
                "---\nalwaysApply: true\n---\n\n# Base\n", encoding="utf-8"
            )

            status = main(["generate", str(project)])

            self.assertEqual(status, 0)
            self.assertTrue((project / ".codebuddy" / "rules" / "demo-project-rules.md").is_file())
            self.assertEqual(
                (project / ".codebuddy" / "rules" / "demo-project-rules.md").read_bytes(),
                (project / ".qoder" / "rules" / "demo-project-rules.md").read_bytes(),
            )

    def test_verify_missing_manifest_returns_one_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()

            with redirect_stdout(output):
                status = main(["verify", directory])

            self.assertEqual(status, 1)
            self.assertIn("MANIFEST", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())


if __name__ == "__main__":
    unittest.main()
