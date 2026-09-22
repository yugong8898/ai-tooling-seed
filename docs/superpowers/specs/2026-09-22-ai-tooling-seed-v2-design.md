# AI Tooling Seed v2 Design

## Goal

Upgrade `ai-tooling-seed` from a manually copied WLYD-derived template into a safe, repeatable frontend-first project bootstrapper. The tool must inspect a target repository, initialize or merge a canonical `.cursor/` configuration, generate compatible CodeBuddy/Qoder artifacts, and verify that generated output has not drifted.

## Scope

Version 2 targets React, Vue, Vite, Next.js, Umi, uni-app, Webpack, TypeScript, JavaScript, Less, Sass/SCSS, and CSS projects. It supports both single-package repositories and monorepos.

The detector records lightweight evidence for Python, Go, Java, and Rust repositories so the architecture remains extensible, but version 2 does not generate framework-specific backend rules.

## Canonical Source Model

`.cursor/` is the only editable source for synchronized AI tooling content:

```text
.cursor/
├── ai-tooling.json
├── prompts/
├── rules/
├── skills/
├── snippets/
├── context/
├── settings.json
└── extensions.json
```

The generator derives these compatibility outputs:

```text
.codebuddy/
.qoder/
.md/prompts/
AGENTS.md managed section
README.md managed section
```

Generated Markdown files carry a warning header. Verification reports direct edits to generated files as drift. `.cursor/settings.json` and `.cursor/extensions.json` remain Cursor-specific canonical files and are not copied into other tools.

## CLI

The dependency-free Python CLI lives at `scripts/ai_tooling.py` and supports:

```bash
python3 scripts/ai_tooling.py detect TARGET
python3 scripts/ai_tooling.py init TARGET [--profile frontend|generic] [--project-name NAME] [--dry-run]
python3 scripts/ai_tooling.py generate TARGET [--dry-run]
python3 scripts/ai_tooling.py verify TARGET
```

`detect` is read-only. `init --dry-run` renders a change plan without writing. `init` merges the canonical Cursor source into the target, writes a manifest, creates generated outputs, and runs verification. `generate` refreshes outputs from an existing manifest. `verify` never changes files.

## Project Detection

Detection searches the repository root and package directories at bounded depth. It reads `package.json` plus well-known configuration and stylesheet filenames. Every detected fact records evidence such as the file and dependency that established it.

The detector may infer:

- repository shape: single package or monorepo;
- package name and relative path;
- language: JavaScript or TypeScript;
- framework and build system;
- UI library and state-management dependencies;
- style systems actually present;
- package-manager and available scripts;
- lightweight non-frontend project markers.

Unknown facts remain explicit `pendingQuestions` entries in `.cursor/ai-tooling.json`. The tool never invents CDN domains, compatibility bans, business conventions, amount-formatting utilities, or API contracts.

## Profiles and Policies

The `frontend` profile supplies neutral frontend rules and prompts. The `generic` profile supplies only language-independent collaboration, verification, and repository guidance.

WLYD-derived policies are not defaults. Rules such as retaining replaced code as comments, response-name probes, mandatory amount utilities, CDN handling, and multi-page business checklists live in an optional `legacy-wlyd` policy pack. Version 2 preserves the pack as documentation/template material but does not enable it automatically.

## Merge and Safety Model

Initialization is conservative and idempotent:

1. Build the complete operation plan in memory.
2. Classify each path as create, managed update, structured merge, unchanged, or conflict.
3. In dry-run mode, print the plan and perform no writes.
4. Before a real write, copy every affected pre-existing file into `.ai-tooling/backups/<UTC timestamp>/`.
5. Apply Markdown updates only inside `<!-- ai-tooling:start -->` and `<!-- ai-tooling:end -->` markers.
6. Merge JSON by key. Existing target values win; seed defaults only fill missing keys.
7. Never overwrite an unrecognized same-path source file. Report it as a conflict and leave it untouched.
8. Write generated files only when they carry the generator marker or do not yet exist.
9. Run verification and return a non-zero status if any conflict, pending required fact, or drift remains.

Repeated initialization must not duplicate managed blocks, recommendations, skills, or prompts.

## Generated Rules

Cursor keeps modular rules. CodeBuddy and Qoder receive a deterministic combined project-rules document assembled from enabled Cursor rules in lexical filename order. CodeBuddy and Qoder rule files must be byte-identical.

Cursor is also canonical for skills, snippets, context, and prompts:

- `.cursor/skills` generates `.codebuddy/skills` and `.qoder/skills`;
- `.cursor/snippets` generates `.codebuddy/snippets`;
- `.cursor/context` generates `.codebuddy/context` and `.qoder/context`;
- `.cursor/prompts` generates `.md/prompts`.

## Verification

`verify` checks:

- manifest schema and required paths;
- valid JSON files;
- no unresolved template placeholders in managed/generated artifacts;
- no filenames illegal on Windows;
- no stale `wlyd`, `yd`, `bondee`, `siren`, or `spatio` residue in default artifacts;
- generated-file hashes against freshly rendered output;
- CodeBuddy/Qoder rule byte equality;
- skills, snippets, context, and prompt mirror completeness;
- required rule frontmatter;
- Markdown relative links within managed artifacts;
- exactly one managed block in `README.md` and `AGENTS.md`;
- no credential-like URL in tracked files.

The legacy `verify-rules-sync.sh` becomes a compatibility wrapper around the Python verifier.

## Errors and Reporting

Commands print concise Chinese summaries and machine-stable status labels: `CREATE`, `UPDATE`, `MERGE`, `UNCHANGED`, `CONFLICT`, `WARNING`, and `ERROR`. Expected validation failures never emit Python tracebacks. `--verbose` is out of scope for version 2.

Exit status is `0` for success, `1` for validation or merge conflicts, and `2` for invalid command usage or an unreadable target.

## Tests

Tests use Python's standard `unittest` and temporary directories. Fixtures cover:

- React/Vite single-package detection;
- Vue monorepo detection;
- lightweight backend marker detection;
- dry-run with zero writes;
- JSON merge preserving existing values;
- Markdown managed-block insertion and replacement;
- conflict backup behavior;
- idempotent repeated initialization;
- deterministic generation and mirror equality;
- placeholder, drift, illegal filename, broken link, and missing-file failures;
- clean error output when canonical files are missing.

The repository adds one top-level test command and CI-friendly exit codes without external dependencies.

## Documentation Migration

The root README becomes the operational quick start. Historical yd/bondee/WLYD incidents move out of the primary onboarding path into a legacy case-study document. The main templates use neutral project language and no longer require monorepo structure, response-name probes, or WLYD-specific business rules.

## Acceptance Criteria

- A new frontend project can be detected, previewed, initialized, regenerated, and verified with documented commands.
- Existing README, AGENTS, Cursor JSON settings, and unrecognized source files are not silently overwritten.
- A second identical initialization produces no file-content changes.
- `.cursor/` is the documented and enforced source for every synchronized artifact.
- Freshly initialized fixtures pass verification.
- The CLI and tests require only Python 3.9 or newer.
