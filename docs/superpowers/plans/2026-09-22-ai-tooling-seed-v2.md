# AI Tooling Seed v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dependency-free CLI that detects frontend project facts, safely initializes a canonical `.cursor/` source, generates CodeBuddy/Qoder compatibility files, and verifies the complete scaffold.

**Architecture:** A small `ai_tooling` Python package separates detection, safe merging, deterministic rendering, and verification. `scripts/ai_tooling.py` is the stable command entrypoint. The existing `.cursor/` tree becomes canonical; generated mirrors are marked and compared against fresh renders.

**Tech Stack:** Python 3.9+ standard library, `unittest`, Bash compatibility wrapper, Markdown/JSON templates.

## Global Constraints

- `.cursor/` is the only editable source for rules, prompts, skills, snippets, context, settings, and extensions.
- Existing target content is never silently overwritten.
- Markdown uses managed blocks; JSON merge preserves target values.
- All real writes back up affected pre-existing files first.
- The CLI has no third-party runtime or test dependency.
- Default profiles are `frontend` and `generic`; backend detection remains lightweight.
- Expected failures return concise diagnostics without tracebacks.

---

### Task 1: Project detection and CLI skeleton

**Files:**
- Create: `ai_tooling/__init__.py`
- Create: `ai_tooling/detect.py`
- Create: `ai_tooling/cli.py`
- Create: `scripts/ai_tooling.py`
- Create: `tests/__init__.py`
- Create: `tests/helpers.py`
- Create: `tests/test_detect.py`
- Create: `tests/test_cli.py`

**Interfaces:**
- Produces: `detect_project(target: Path) -> dict[str, object]`
- Produces: `main(argv: Sequence[str] | None = None) -> int`
- Produces: CLI command `detect TARGET`

- [ ] **Step 1: Write failing detection tests**

Create fixtures with real `package.json` and style/config files. Assert React/Vite single-package detection, Vue workspace package discovery, and lightweight `pyproject.toml` marker detection:

```python
report = detect_project(project)
self.assertEqual(report["shape"], "single-package")
self.assertEqual(report["packages"][0]["frameworks"], ["react"])
self.assertIn("vite", report["packages"][0]["buildTools"])
self.assertIn("scss", report["packages"][0]["styles"])
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_detect tests.test_cli -v`

Expected: import failure because `ai_tooling.detect` and CLI entrypoint do not exist.

- [ ] **Step 3: Implement bounded evidence-based detection**

Implement JSON-safe helpers and deterministic sorted output. Inspect root plus package directories discovered from workspace globs and bounded `package.json` search. Map dependencies to frameworks/build tools/UI/state systems and stylesheet suffixes. Record evidence strings. Do not infer business facts.

- [ ] **Step 4: Implement CLI parsing and clean error handling**

Use `argparse`. Return `2` for missing/unreadable targets. Serialize detect output with UTF-8 Chinese preserved and stable indentation. Catch expected `OSError`, `ValueError`, and JSON decode failures in `main` so users do not receive tracebacks.

- [ ] **Step 5: Run tests and confirm GREEN**

Run: `python3 -m unittest tests.test_detect tests.test_cli -v`

Expected: all Task 1 tests pass.

- [ ] **Step 6: Commit**

```bash
git add ai_tooling scripts/ai_tooling.py tests
git commit -m "feat: detect target project stacks"
```

---

### Task 2: Safe merge planning, dry-run, and backups

**Files:**
- Create: `ai_tooling/merge.py`
- Create: `tests/test_merge.py`
- Modify: `ai_tooling/cli.py`

**Interfaces:**
- Produces: `merge_managed_markdown(existing: str, generated: str) -> str`
- Produces: `merge_json_defaults(existing: object, defaults: object) -> object`
- Produces: `Operation(path: Path, action: str, content: bytes | None, reason: str)`
- Produces: `apply_operations(target: Path, operations: Sequence[Operation], dry_run: bool) -> ApplyResult`

- [ ] **Step 1: Write failing merge tests**

Cover insertion/replacement of one managed block, duplicate-marker rejection, recursive JSON defaults where existing values win, dry-run zero writes, backup creation, and refusal to overwrite an unmanaged generated path.

```python
merged = merge_json_defaults(
    {"editor.tabSize": 4, "files": {"trim": True}},
    {"editor.tabSize": 2, "files": {"eol": "\n"}},
)
self.assertEqual(merged["editor.tabSize"], 4)
self.assertEqual(merged["files"], {"trim": True, "eol": "\n"})
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_merge -v`

Expected: import failure because `ai_tooling.merge` does not exist.

- [ ] **Step 3: Implement pure merge functions and operation model**

Use immutable dataclasses. Managed markers are exactly `<!-- ai-tooling:start -->` and `<!-- ai-tooling:end -->`. Reject unbalanced or duplicate blocks with a typed `MergeConflict`. Recursively merge dictionaries; keep existing lists and scalar values.

- [ ] **Step 4: Implement transactional-style application**

Build all operations before writing. Back up every changed pre-existing path beneath one `.ai-tooling/backups/YYYYMMDDTHHMMSSZ/` directory, preserving relative paths. Use temporary sibling files plus `Path.replace` for file writes. Conflicts are reported and never written.

- [ ] **Step 5: Add `init --dry-run` command wiring**

The initial command may create only the manifest and managed README/AGENTS sections; later tasks add generated mirrors. Print stable action labels and return `1` when conflicts exist.

- [ ] **Step 6: Run tests and confirm GREEN**

Run: `python3 -m unittest tests.test_merge tests.test_cli -v`

Expected: all Task 2 tests pass.

- [ ] **Step 7: Commit**

```bash
git add ai_tooling tests
git commit -m "feat: add safe idempotent project merging"
```

---

### Task 3: Canonical Cursor rendering and mirror generation

**Files:**
- Create: `ai_tooling/render.py`
- Create: `tests/test_render.py`
- Modify: `ai_tooling/cli.py`
- Create: `.cursor/ai-tooling.json`
- Create: `.cursor/prompts/README.md`
- Move: `.md/prompts/*.md` to `.cursor/prompts/*.md`
- Modify: `.cursor/rules/core-general-standards.mdc`
- Modify: `.cursor/rules/core-project-rules.mdc`
- Modify: `.cursor/rules/core-ai-collaboration.mdc`
- Modify: `.cursor/rules/ref-tech-stack.mdc`
- Remove: `.md/prompts/stack-<type>.md`

**Interfaces:**
- Produces: `load_manifest(target: Path) -> Manifest`
- Produces: `render_generated_files(source_root: Path, target_root: Path, manifest: Manifest) -> dict[Path, bytes]`
- Produces: CLI command `generate TARGET [--dry-run]`

- [ ] **Step 1: Write failing rendering tests**

Assert deterministic project-rule assembly, byte-identical CodeBuddy/Qoder rules, complete skill/snippet/context/prompt mirrors, generated headers, project-name substitution, and unchanged output on a second generation.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_render -v`

Expected: import failure because `ai_tooling.render` does not exist.

- [ ] **Step 3: Implement manifest parsing and token rendering**

Use a versioned JSON manifest with exact fields `schemaVersion`, `projectName`, `profile`, `enabledPolicies`, `detected`, and `pendingQuestions`. Support the generator token `{{PROJECT_NAME}}` only in canonical source files; generated output must contain no generator tokens.

- [ ] **Step 4: Implement deterministic compatibility output**

Combine enabled Cursor `core-*.mdc` bodies in lexical order into one generated project-rules file. Copy skill trees to both CodeBuddy and Qoder, snippets to CodeBuddy, contexts to both, and prompts to `.md/prompts`. Exclude editor-only JSON. Put a generated warning in Markdown outputs.

- [ ] **Step 5: Migrate seed content to `.cursor` authority**

Move role/stack prompts to `.cursor/prompts`, rename the illegal `stack-<type>.md` path to `stack-template.md`, remove project-specific defaults, and make the base rules neutral. Preserve WLYD-only guidance in a disabled policy document rather than always-applied rules.

- [ ] **Step 6: Wire `init` and `generate`**

`init` combines detection with seed canonical templates, writes target `.cursor` source conservatively, then generates mirrors. `generate` requires an existing manifest and canonical source.

- [ ] **Step 7: Run tests and confirm GREEN**

Run: `python3 -m unittest tests.test_render tests.test_merge tests.test_cli -v`

Expected: all Task 3 tests pass.

- [ ] **Step 8: Commit**

```bash
git add ai_tooling .cursor .md .codebuddy .qoder tests
git commit -m "feat: generate tooling from cursor source"
```

---

### Task 4: Full verification and compatibility wrapper

**Files:**
- Create: `ai_tooling/verify.py`
- Create: `tests/test_verify.py`
- Modify: `ai_tooling/cli.py`
- Modify: `scripts/verify-rules-sync.sh`

**Interfaces:**
- Produces: `verify_project(target: Path) -> VerificationResult`
- Produces: CLI command `verify TARGET`

- [ ] **Step 1: Write failing verifier tests**

Build a clean generated fixture and one mutation per failure class: drift, unresolved generator token, illegal filename, stale project residue, invalid JSON, missing mirror, non-identical rules, broken relative link, duplicate managed block, and credential-like tracked content.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_verify -v`

Expected: import failure because `ai_tooling.verify` does not exist.

- [ ] **Step 3: Implement structured checks**

Return a list of `VerificationIssue(code, path, message)`. Render expected generated output in memory and compare bytes. Restrict placeholder and residue scanning to managed/generated artifacts so legitimate project prose is not rejected. Validate relative Markdown links without network access.

- [ ] **Step 4: Wire CLI and shell wrapper**

Print each issue with stable code and return `1`; print one success summary and return `0`. Make `verify-rules-sync.sh` locate the repository Python entrypoint and delegate without traceback-prone inline Python.

- [ ] **Step 5: Run tests and confirm GREEN**

Run: `python3 -m unittest tests.test_verify tests.test_render tests.test_merge tests.test_detect tests.test_cli -v`

Expected: all Task 4 tests pass.

- [ ] **Step 6: Commit**

```bash
git add ai_tooling scripts tests
git commit -m "feat: verify generated tooling integrity"
```

---

### Task 5: Operational docs, legacy extraction, and end-to-end acceptance

**Files:**
- Modify: `README.md`
- Modify: `templates/AGENTS.md`
- Modify: `templates/PROJECT-README.md`
- Create: `docs/legacy/wlyd-derived-practices.md`
- Modify: `项目技术栈文档体系搭建与维护手册.md`
- Create: `tests/test_end_to_end.py`
- Create: `.gitignore`

**Interfaces:**
- Produces: documented quick-start commands matching the CLI
- Produces: end-to-end fixture acceptance test

- [ ] **Step 1: Write failing end-to-end tests**

From a React/Vite fixture with existing README, AGENTS, and Cursor JSON settings, call `init`, `verify`, call `init` again, and assert the second content snapshot is byte-identical. Assert existing prose and JSON values survive and no WLYD residue or illegal filename exists.

- [ ] **Step 2: Run test and confirm RED**

Run: `python3 -m unittest tests.test_end_to_end -v`

Expected: failure until final template and documentation migration is complete.

- [ ] **Step 3: Rewrite operational documentation**

Make the root README the concise source for prerequisites, detect, dry-run, init, generate, verify, merge rules, recovery, and profile behavior. Correct the former six/seven-step mismatch. Document Python 3.9+.

- [ ] **Step 4: Neutralize generated document templates**

Remove mandatory monorepo language, probes, hard-coded seven-skill/four-snippet counts, and Cursor/CodeBuddy source contradictions. Use managed blocks compatible with the merger.

- [ ] **Step 5: Extract historical practices**

Move WLYD/yd/bondee incident history and optional legacy policies to `docs/legacy/wlyd-derived-practices.md`. Reduce the maintenance handbook to current v2 architecture and workflows, linking to the legacy document for context.

- [ ] **Step 6: Ignore local artifacts**

Add `.DS_Store`, `__pycache__/`, `*.pyc`, and `.ai-tooling/backups/` to `.gitignore`.

- [ ] **Step 7: Run all tests and acceptance commands**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ai_tooling.py detect .
python3 scripts/ai_tooling.py verify .
bash scripts/verify-rules-sync.sh .
git diff --check
```

Expected: tests pass, both verifiers exit `0`, and `git diff --check` emits no output.

- [ ] **Step 8: Commit**

```bash
git add README.md templates docs 项目技术栈文档体系搭建与维护手册.md tests .gitignore
git commit -m "docs: publish safe v2 onboarding workflow"
```

---

### Task 6: Final review and remediation

**Files:**
- Modify: files identified by review, if any

**Interfaces:**
- Consumes: complete implementation and design specification
- Produces: reviewed, verified release candidate

- [ ] **Step 1: Review requirements against the design**

Check every acceptance criterion in `docs/superpowers/specs/2026-09-22-ai-tooling-seed-v2-design.md` against code, tests, and documentation.

- [ ] **Step 2: Request focused code review**

Provide the reviewer the design, plan, base commit `aac4eb1`, current HEAD, and explicit focus areas: overwrite safety, idempotency, path traversal, generated-source direction, and false-positive verification.

- [ ] **Step 3: Fix all Critical and Important findings with TDD**

For each behavior bug, add a failing regression test, run it to confirm RED, implement the smallest fix, and rerun the relevant tests.

- [ ] **Step 4: Run fresh final verification**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ai_tooling.py verify .
bash scripts/verify-rules-sync.sh .
git diff --check
git status --short
```

Expected: zero test failures, verifier success, no whitespace errors, and only intentional changes shown by status.
