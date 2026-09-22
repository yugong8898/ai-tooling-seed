from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_tooling.render import GENERATED_MARKER, load_manifest, render_generated_files
from tests.helpers import write_json, write_text


class RenderTests(unittest.TestCase):
    def _canonical_project(self, root: Path) -> None:
        write_json(
            root / ".cursor" / "ai-tooling.json",
            {
                "schemaVersion": 2,
                "projectName": "demo-web",
                "profile": "frontend",
                "enabledPolicies": [],
                "detected": {"shape": "single-package", "packages": []},
                "pendingQuestions": [],
            },
        )
        write_text(
            root / ".cursor" / "rules" / "core-a.mdc",
            "---\nalwaysApply: true\n---\n\n# {{PROJECT_NAME}} Core A\n\nRule A.\n",
        )
        write_text(
            root / ".cursor" / "rules" / "core-b.mdc",
            "---\nalwaysApply: true\n---\n\n# Core B\n\nRule B.\n",
        )
        write_text(root / ".cursor" / "skills" / "review" / "SKILL.md", "# Review {{PROJECT_NAME}}\n")
        write_text(root / ".cursor" / "snippets" / "api.md", "# API\n")
        write_text(root / ".cursor" / "context" / "terms.md", "# Terms\n")
        write_text(root / ".cursor" / "prompts" / "role-coder.md", "# Coder {{PROJECT_NAME}}\n")

    def test_renders_deterministic_complete_mirrors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._canonical_project(root)

            manifest = load_manifest(root)
            first = render_generated_files(root, root, manifest)
            second = render_generated_files(root, root, manifest)

            self.assertEqual(first, second)
            codebuddy_rule = first[Path(".codebuddy/rules/demo-web-project-rules.md")]
            self.assertEqual(codebuddy_rule, first[Path(".qoder/rules/demo-web-project-rules.md")])
            self.assertLess(codebuddy_rule.index(b"Rule A."), codebuddy_rule.index(b"Rule B."))
            self.assertIn(b"demo-web Core A", codebuddy_rule)
            self.assertEqual(
                first[Path(".codebuddy/skills/review/SKILL.md")],
                first[Path(".qoder/skills/review/SKILL.md")],
            )
            self.assertIn(Path(".codebuddy/snippets/api.md"), first)
            self.assertNotIn(Path(".qoder/snippets/api.md"), first)
            self.assertIn(Path(".qoder/context/terms.md"), first)
            self.assertIn(Path(".md/prompts/role-coder.md"), first)
            self.assertTrue(first[Path(".md/prompts/role-coder.md")].decode().startswith(GENERATED_MARKER))

    def test_rejects_invalid_manifest_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_json(root / ".cursor" / "ai-tooling.json", {"schemaVersion": 1, "projectName": "demo"})

            with self.assertRaisesRegex(ValueError, "schemaVersion"):
                load_manifest(root)


if __name__ == "__main__":
    unittest.main()
