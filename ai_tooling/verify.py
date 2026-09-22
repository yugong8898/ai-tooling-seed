from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from ai_tooling.merge import END_MARKER, START_MARKER
from ai_tooling.render import load_manifest, render_generated_files


WINDOWS_ILLEGAL = re.compile(r"[<>:\"\\|?*]")
PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}|<项目名>|<proj>|<sub[^>]*>|<YYYY[^>]*>|\[占位符\]", re.I)
STALE_PROJECT = re.compile(r"\b(?:wlyd|bondee|yd|siren|spatio)\b", re.I)
CREDENTIAL_URL = re.compile(r"https?://[^/\s:@]+:[^@\s/]+@", re.I)
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MANAGED_ROOTS = (
    Path(".cursor/rules"),
    Path(".cursor/prompts"),
    Path(".cursor/skills"),
    Path(".cursor/snippets"),
    Path(".cursor/context"),
    Path(".codebuddy"),
    Path(".qoder"),
    Path(".md/prompts"),
)


@dataclass(frozen=True)
class VerificationIssue:
    code: str
    path: Path
    message: str


@dataclass(frozen=True)
class VerificationResult:
    issues: tuple[VerificationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


def _managed_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for relative in MANAGED_ROOTS:
        directory = root / relative
        if directory.is_dir():
            files.update(path for path in directory.rglob("*") if path.is_file() and path.name != ".DS_Store")
    for name in ("README.md", "AGENTS.md"):
        path = root / name
        if path.is_file():
            files.add(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def _text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _check_links(root: Path, path: Path, text: str) -> list[VerificationIssue]:
    issues: list[VerificationIssue] = []
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().split("#", 1)[0]
        if not target or target.startswith(("#", "http://", "https://", "mailto:", "data:")):
            continue
        target = target.strip("<>")
        if not (path.parent / target).resolve().exists():
            issues.append(VerificationIssue("BROKEN_LINK", path.relative_to(root), f"相对链接不存在：{raw_target}"))
    return issues


def verify_project(target: Path) -> VerificationResult:
    root = target.expanduser().resolve()
    issues: list[VerificationIssue] = []
    try:
        manifest = load_manifest(root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return VerificationResult((VerificationIssue("MANIFEST", Path(".cursor/ai-tooling.json"), str(error)),))

    try:
        expected = render_generated_files(root, root, manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return VerificationResult((VerificationIssue("RENDER", Path(".cursor"), str(error)),))

    for relative, content in expected.items():
        path = root / relative
        if not path.is_file():
            issues.append(VerificationIssue("MISSING_GENERATED", relative, "缺少从 .cursor 生成的文件"))
        elif path.read_bytes() != content:
            issues.append(VerificationIssue("GENERATED_DRIFT", relative, "生成物与 .cursor 权威源不一致"))

    for json_path in (root / ".cursor").rglob("*.json"):
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            issues.append(VerificationIssue("INVALID_JSON", json_path.relative_to(root), str(error)))

    for path in _managed_files(root):
        relative = path.relative_to(root)
        if any(WINDOWS_ILLEGAL.search(part) for part in relative.parts):
            issues.append(VerificationIssue("ILLEGAL_FILENAME", relative, "文件名包含 Windows 不支持的字符"))
        text = _text(path)
        if text is None:
            continue
        if PLACEHOLDER.search(text):
            issues.append(VerificationIssue("UNRESOLVED_PLACEHOLDER", relative, "存在未解析模板占位符"))
        if STALE_PROJECT.search(text):
            issues.append(VerificationIssue("STALE_PROJECT_RESIDUE", relative, "默认产物包含旧项目标识"))
        if CREDENTIAL_URL.search(text):
            issues.append(VerificationIssue("CREDENTIAL_URL", relative, "检测到 URL 内嵌凭据"))
        if path.suffix.lower() in {".md", ".mdc"}:
            issues.extend(_check_links(root, path, text))

    for name in ("README.md", "AGENTS.md"):
        path = root / name
        if not path.is_file():
            issues.append(VerificationIssue("MANAGED_BLOCK_COUNT", Path(name), "缺少文档或 ai-tooling 受控区块"))
            continue
        text = path.read_text(encoding="utf-8")
        if text.count(START_MARKER) != 1 or text.count(END_MARKER) != 1:
            issues.append(VerificationIssue("MANAGED_BLOCK_COUNT", Path(name), "受控区块必须且只能出现一次"))

    rules_directory = root / ".cursor" / "rules"
    if rules_directory.is_dir():
        for path in rules_directory.glob("core-*.mdc"):
            if "alwaysApply: true" not in "\n".join(path.read_text(encoding="utf-8").splitlines()[:4]):
                issues.append(VerificationIssue("RULE_FRONTMATTER", path.relative_to(root), "core 规则缺少 alwaysApply: true"))

    unique = {(item.code, item.path.as_posix(), item.message): item for item in issues}
    ordered = tuple(unique[key] for key in sorted(unique))
    return VerificationResult(ordered)
