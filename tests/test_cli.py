from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ai_tooling.cli import main
from tests.helpers import write_json


class CliTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
