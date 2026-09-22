from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from ai_tooling.detect import detect_project
from ai_tooling.merge import MergeConflict, Operation, apply_operations, merge_json_defaults, merge_managed_markdown


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
    return parser


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _init_operations(target: Path, profile: str, project_name: str | None) -> list[Operation]:
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


def _print_operations(operations: Sequence[Operation]) -> None:
    for operation in operations:
        print(f"{operation.action:<9} {operation.path}  {operation.reason}")


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
            operations = _init_operations(target, args.profile, args.project_name)
            _print_operations(operations)
            result = apply_operations(target, operations, dry_run=args.dry_run)
            return 1 if result.conflicts else 0
    except (OSError, ValueError, MergeConflict, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 2
