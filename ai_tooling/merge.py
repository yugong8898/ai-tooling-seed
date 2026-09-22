from __future__ import annotations

import copy
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


START_MARKER = "<!-- ai-tooling:start -->"
END_MARKER = "<!-- ai-tooling:end -->"


class MergeConflict(ValueError):
    """Raised when existing content cannot be merged without data loss."""


@dataclass(frozen=True)
class Operation:
    path: Path
    action: str
    content: bytes | None
    reason: str

    def __post_init__(self) -> None:
        if self.path.is_absolute() or ".." in self.path.parts:
            raise ValueError(f"操作路径必须位于目标目录内：{self.path}")
        if self.action not in {"CREATE", "UPDATE", "MERGE", "UNCHANGED", "CONFLICT"}:
            raise ValueError(f"未知操作类型：{self.action}")


@dataclass(frozen=True)
class ApplyResult:
    changed: int
    conflicts: int
    backup_root: Path | None
    operations: tuple[Operation, ...]


def merge_managed_markdown(existing: str, generated: str) -> str:
    starts = existing.count(START_MARKER)
    ends = existing.count(END_MARKER)
    if starts != ends or starts > 1:
        raise MergeConflict("Markdown 中的 ai-tooling 受控区块标记不平衡或重复")

    block = f"{START_MARKER}\n{generated.strip()}\n{END_MARKER}"
    if starts == 0:
        prefix = existing.rstrip()
        return f"{prefix}\n\n{block}\n" if prefix else f"{block}\n"

    start = existing.index(START_MARKER)
    end = existing.index(END_MARKER, start) + len(END_MARKER)
    return f"{existing[:start]}{block}{existing[end:]}".rstrip() + "\n"


def merge_json_defaults(existing: object, defaults: object) -> object:
    if not isinstance(existing, dict) or not isinstance(defaults, dict):
        return copy.deepcopy(existing)
    merged = copy.deepcopy(existing)
    for key, default_value in defaults.items():
        if key not in merged:
            merged[key] = copy.deepcopy(default_value)
        elif isinstance(merged[key], dict) and isinstance(default_value, dict):
            merged[key] = merge_json_defaults(merged[key], default_value)
    return merged


def _timestamp(now: datetime | None) -> str:
    value = now or datetime.now(timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _safe_destination(root: Path, relative: Path) -> Path:
    """Return a destination only when no nested symlink can escape ``root``."""
    destination = root / relative
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise MergeConflict(f"拒绝通过符号链接写入目标目录外：{relative}")
    try:
        destination.resolve(strict=False).relative_to(root)
    except ValueError as error:
        raise MergeConflict(f"操作路径越界：{relative}") from error
    return destination


def apply_operations(
    target: Path,
    operations: Sequence[Operation],
    *,
    dry_run: bool,
    now: datetime | None = None,
) -> ApplyResult:
    root = target.resolve()
    changed_operations = [item for item in operations if item.action in {"CREATE", "UPDATE", "MERGE"}]
    conflicts = sum(item.action == "CONFLICT" for item in operations)
    backup_root: Path | None = None

    destinations = {item.path: _safe_destination(root, item.path) for item in operations}
    if changed_operations:
        _safe_destination(root, Path(".ai-tooling/backups"))

    if not dry_run and changed_operations:
        existing = [item for item in changed_operations if destinations[item.path].is_file()]
        if existing:
            timestamp = _timestamp(now)
            backup_relative = Path(".ai-tooling") / "backups" / timestamp
            backup_root = root / backup_relative
            if backup_root.exists() or backup_root.is_symlink():
                raise MergeConflict(f"备份目录已存在，拒绝复用：{backup_relative}")
            backup_destinations = {
                item.path: _safe_destination(root, backup_relative / item.path) for item in existing
            }
            for item in existing:
                source = destinations[item.path]
                destination = backup_destinations[item.path]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        for item in changed_operations:
            if item.content is None:
                raise ValueError(f"{item.action} 操作缺少内容：{item.path}")
            _write_atomic(destinations[item.path], item.content)

    return ApplyResult(
        changed=len(changed_operations),
        conflicts=conflicts,
        backup_root=backup_root,
        operations=tuple(operations),
    )
