from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from ai_tooling.detect import detect_project


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-tooling", description="安全初始化和校验项目 AI 工具配置")
    subcommands = parser.add_subparsers(dest="command", required=True)
    detect = subcommands.add_parser("detect", help="只读识别目标项目")
    detect.add_argument("target", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "detect":
            report = detect_project(args.target)
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 2
