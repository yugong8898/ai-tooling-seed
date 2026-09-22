from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_tooling.detect import detect_project
from tests.helpers import write_json, write_text


class DetectProjectTests(unittest.TestCase):
    def test_detects_react_vite_single_package_with_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(
                project / "package.json",
                {
                    "name": "shop-web",
                    "scripts": {"dev": "vite", "build": "vite build"},
                    "dependencies": {"react": "^18.3.0", "zustand": "^4.5.0"},
                    "devDependencies": {"vite": "^5.4.0", "typescript": "^5.5.0"},
                },
            )
            write_text(project / "src" / "app.scss", ".app {}\n")

            report = detect_project(project)

            self.assertEqual(report["projectName"], "shop-web")
            self.assertEqual(report["shape"], "single-package")
            package = report["packages"][0]
            self.assertEqual(package["frameworks"], ["react"])
            self.assertIn("vite", package["buildTools"])
            self.assertIn("typescript", package["languages"])
            self.assertEqual(package["styles"], ["scss"])
            self.assertTrue(any("package.json" in item for item in package["evidence"]))

    def test_detects_vue_workspace_packages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(
                project / "package.json",
                {"name": "workspace", "private": True, "workspaces": ["apps/*"]},
            )
            write_json(
                project / "apps" / "admin" / "package.json",
                {
                    "name": "admin",
                    "dependencies": {"vue": "^3.5.0", "pinia": "^2.2.0"},
                    "devDependencies": {"vite": "^6.0.0"},
                },
            )
            write_text(project / "apps" / "admin" / "src" / "main.less", "@x: 1;\n")

            report = detect_project(project)

            self.assertEqual(report["shape"], "monorepo")
            package = next(item for item in report["packages"] if item["path"] == "apps/admin")
            self.assertEqual(package["frameworks"], ["vue"])
            self.assertEqual(package["stateManagement"], ["pinia"])
            self.assertEqual(package["styles"], ["less"])

    def test_records_lightweight_backend_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_text(project / "pyproject.toml", "[project]\nname = 'service'\n")
            write_text(project / "go.mod", "module example.test/service\n")

            report = detect_project(project)

            self.assertEqual(report["shape"], "repository")
            self.assertEqual(report["backendMarkers"], ["go", "python"])
            self.assertEqual(report["packages"], [])


if __name__ == "__main__":
    unittest.main()
