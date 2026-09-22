from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from ai_tooling.detect import detect_project
from ai_tooling.merge import MergeConflict, Operation, apply_operations, merge_json_defaults, merge_managed_markdown
from ai_tooling.render import GENERATED_MARKER, Manifest, load_manifest, render_generated_files, render_tokens
from ai_tooling.verify import verify_project


SEED_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIRECTORIES = ("rules", "prompts", "skills", "snippets", "context")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-tooling", description="安全初始化和校验项目 AI 工具配置")
    subcommands = parser.add_subparsers(dest="command", required=True)
    detect = subcommands.add_parser("detect", help="只读识别目标项目")
    detect.add_argument("target", type=Path)
    init = subcommands.add_parser("init", help="安全初始化目标项目")
    init.add_argument("target", type=Path)
    init.add_argument("--profile", choices=("frontend", "generic"), default="frontend")
    init.add_argument("--project-name")
    init.add_argument("--dry-run", action="store_true")
    generate = subcommands.add_parser("generate", help="从 .cursor 权威源刷新兼容文件")
    generate.add_argument("target", type=Path)
    generate.add_argument("--dry-run", action="store_true")
    verify = subcommands.add_parser("verify", help="校验权威源、生成物和项目入口")
    verify.add_argument("target", type=Path)
    return parser


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _manifest_defaults(target: Path, profile: str, project_name: str | None) -> tuple[dict[str, object], dict[str, object]]:
    report = detect_project(target)
    name = project_name or str(report["projectName"])
    manifest_defaults = {
        "schemaVersion": 2,
        "projectName": name,
        "profile": profile,
        "enabledPolicies": [],
        "detected": {key: value for key, value in report.items() if key not in {"root", "projectName", "pendingQuestions"}},
        "pendingQuestions": report["pendingQuestions"],
    }
    return manifest_defaults, report


def _init_operations(target: Path, profile: str, project_name: str | None) -> list[Operation]:
    manifest_defaults, _ = _manifest_defaults(target, profile, project_name)
    name = str(manifest_defaults["projectName"])
    operations: list[Operation] = []
    manifest_path = target / ".cursor" / "ai-tooling.json"
    if manifest_path.is_file():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        merged = merge_json_defaults(existing, manifest_defaults)
        content = _json_bytes(merged)
        action = "UNCHANGED" if manifest_path.read_bytes() == content else "MERGE"
    else:
        content = _json_bytes(manifest_defaults)
        action = "CREATE"
    operations.append(Operation(Path(".cursor/ai-tooling.json"), action, content, "Cursor 权威源清单"))

    managed_documents = {
        "README.md": f"## AI 工具配置\n\n本项目使用 `.cursor/` 作为唯一配置源。项目：`{name}`；profile：`{profile}`。",
        "AGENTS.md": "## AI 工具协作入口\n\n开始工作前读取 `.cursor/ai-tooling.json` 与 `.cursor/rules/`；生成目录不得直接编辑。",
    }
    for relative, generated in managed_documents.items():
        path = target / relative
        existing = path.read_text(encoding="utf-8") if path.is_file() else ""
        merged = merge_managed_markdown(existing, generated).encode("utf-8")
        if not path.exists():
            action = "CREATE"
        elif path.read_bytes() == merged:
            action = "UNCHANGED"
        else:
            action = "MERGE"
        operations.append(Operation(Path(relative), action, merged, "更新 ai-tooling 受控区块"))
    return operations


def _manifest_from_defaults(value: dict[str, object]) -> Manifest:
    return Manifest(
        schema_version=2,
        project_name=str(value["projectName"]),
        profile=str(value["profile"]),
        enabled_policies=tuple(str(item) for item in value["enabledPolicies"]),
        detected=dict(value["detected"]),
        pending_questions=tuple(value["pendingQuestions"]),
    )


def _canonical_source_operations(target: Path, manifest: Manifest) -> list[Operation]:
    operations: list[Operation] = []
    source_cursor = SEED_ROOT / ".cursor"
    if manifest.profile == "frontend":
        sources: list[Path] = [source_cursor / "settings.json", source_cursor / "extensions.json"]
        directories = CANONICAL_DIRECTORIES
    else:
        sources = []
        directories = ("rules", "skills", "context")
    for directory in directories:
        root = source_cursor / directory
        if root.is_dir():
            sources.extend(path for path in root.rglob("*") if path.is_file() and path.name != ".DS_Store")
    for source in sorted(sources, key=lambda path: path.relative_to(source_cursor).as_posix()):
        relative = Path(".cursor") / source.relative_to(source_cursor)
        destination = target / relative
        if source.suffix == ".json":
            defaults = json.loads(source.read_text(encoding="utf-8"))
            if destination.is_file():
                existing = json.loads(destination.read_text(encoding="utf-8"))
                content = _json_bytes(merge_json_defaults(existing, defaults))
                action = "UNCHANGED" if destination.read_bytes() == content else "MERGE"
            else:
                content = _json_bytes(defaults)
                action = "CREATE"
        else:
            raw = source.read_bytes()
            if source.suffix.lower() in {".md", ".mdc", ".txt"}:
                raw = render_tokens(raw.decode("utf-8"), manifest).encode("utf-8")
            content = raw
            if not destination.exists():
                action = "CREATE"
            elif destination.read_bytes() == content:
                action = "UNCHANGED"
            else:
                action = "UNCHANGED"
                content = destination.read_bytes()
        operations.append(Operation(relative, action, content, "初始化 .cursor 权威源；已有同名源保留"))
    return operations


def _print_operations(operations: Sequence[Operation]) -> None:
    for operation in operations:
        print(f"{operation.action:<9} {operation.path}  {operation.reason}")


def _operations_for_generated(target: Path, generated: dict[Path, bytes]) -> list[Operation]:
    operations: list[Operation] = []
    for relative, content in generated.items():
        path = target / relative
        if not path.exists():
            action = "CREATE"
            reason = "从 .cursor 生成"
        elif path.read_bytes() == content:
            action = "UNCHANGED"
            reason = "生成物未变化"
        elif path.suffix.lower() in {".md", ".mdc", ".txt"} and GENERATED_MARKER in path.read_text(
            encoding="utf-8", errors="replace"
        ):
            action = "UPDATE"
            reason = "刷新受管生成物"
        else:
            action = "CONFLICT"
            content = None
            reason = "同名文件不是 ai-tooling 生成物"
        operations.append(Operation(relative, action, content, reason))
    return operations


def _generation_operations(target: Path) -> list[Operation]:
    manifest = load_manifest(target)
    return _operations_for_generated(target, render_generated_files(target, target, manifest))


def _print_verification(target: Path) -> int:
    result = verify_project(target)
    if result.ok:
        print("OK: AI tooling 配置完整且与 .cursor 权威源一致")
        return 0
    for issue in result.issues:
        print(f"{issue.code:<24} {issue.path}  {issue.message}")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "detect":
            report = detect_project(args.target)
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.command == "init":
            target = args.target.expanduser().resolve()
            manifest_defaults, _ = _manifest_defaults(target, args.profile, args.project_name)
            manifest = _manifest_from_defaults(manifest_defaults)
            base_operations = _init_operations(target, args.profile, args.project_name)
            source_operations = _canonical_source_operations(target, manifest)
            _print_operations(base_operations + source_operations)
            base_result = apply_operations(target, base_operations + source_operations, dry_run=args.dry_run)
            if args.dry_run:
                generated = render_generated_files(SEED_ROOT, target, manifest)
                generation_operations = _operations_for_generated(target, generated)
            else:
                generation_operations = _generation_operations(target)
            _print_operations(generation_operations)
            generated_result = apply_operations(target, generation_operations, dry_run=args.dry_run)
            if base_result.conflicts or generated_result.conflicts:
                return 1
            return 0 if args.dry_run else _print_verification(target)
        if args.command == "generate":
            target = args.target.expanduser().resolve()
            operations = _generation_operations(target)
            _print_operations(operations)
            result = apply_operations(target, operations, dry_run=args.dry_run)
            return 1 if result.conflicts else 0
        if args.command == "verify":
            return _print_verification(args.target)
    except (OSError, ValueError, MergeConflict, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 2
