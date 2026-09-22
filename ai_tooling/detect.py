from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


SKIP_DIRECTORIES = {".git", ".worktrees", "node_modules", "dist", "build", "coverage", "vendor"}
STYLE_SUFFIXES = {".css": "css", ".less": "less", ".sass": "sass", ".scss": "scss"}
DEPENDENCY_GROUPS = {
    "frameworks": {
        "react": "react",
        "next": "next",
        "vue": "vue",
        "@dcloudio/uni-app": "uni-app",
        "@tarojs/taro": "taro",
    },
    "buildTools": {
        "vite": "vite",
        "webpack": "webpack",
        "umi": "umi",
        "@umijs/max": "umi",
        "next": "next",
        "@dcloudio/vite-plugin-uni": "vite",
    },
    "uiLibraries": {
        "antd": "antd",
        "@ant-design/vue": "ant-design-vue",
        "element-ui": "element-ui",
        "element-plus": "element-plus",
        "@mui/material": "mui",
        "uview-ui": "uview",
    },
    "stateManagement": {
        "redux": "redux",
        "@reduxjs/toolkit": "redux-toolkit",
        "zustand": "zustand",
        "pinia": "pinia",
        "vuex": "vuex",
        "mobx": "mobx",
        "dva": "dva",
    },
}
BACKEND_MARKERS = {
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "go.mod": "go",
    "pom.xml": "java",
    "build.gradle": "java",
    "build.gradle.kts": "java",
    "Cargo.toml": "rust",
}


def _relative_depth(root: Path, path: Path) -> int:
    return len(path.relative_to(root).parts)


def _is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRECTORIES for part in path.parts)


def _package_files(root: Path, max_depth: int = 4) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("package.json"):
        if _is_skipped(path.relative_to(root)) or _relative_depth(root, path) > max_depth + 1:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def _load_package(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} 必须包含 JSON 对象")
    return value


def _dependency_names(package: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        section = package.get(key, {})
        if isinstance(section, dict):
            names.update(str(name) for name in section)
    return names


def _matched(dependencies: set[str], mapping: dict[str, str]) -> list[str]:
    return sorted({label for dependency, label in mapping.items() if dependency in dependencies})


def _style_systems(package_root: Path, max_depth: int = 6) -> list[str]:
    found: set[str] = set()
    for path in package_root.rglob("*"):
        if not path.is_file() or _is_skipped(path.relative_to(package_root)):
            continue
        if _relative_depth(package_root, path) > max_depth:
            continue
        label = STYLE_SUFFIXES.get(path.suffix.lower())
        if label:
            found.add(label)
    return sorted(found)


def _scripts(package: dict[str, Any]) -> list[str]:
    scripts = package.get("scripts", {})
    return sorted(str(key) for key in scripts) if isinstance(scripts, dict) else []


def _package_report(root: Path, package_file: Path) -> dict[str, object]:
    package = _load_package(package_file)
    dependencies = _dependency_names(package)
    package_root = package_file.parent
    relative = package_root.relative_to(root).as_posix() or "."
    languages = ["typescript"] if "typescript" in dependencies or any(
        item.suffix in {".ts", ".tsx"}
        for item in package_root.glob("*.ts")
    ) else ["javascript"]
    evidence = [f"{package_file.relative_to(root).as_posix()}: dependencies/scripts"]
    styles = _style_systems(package_root)
    if styles:
        evidence.append(f"{relative}: style files ({', '.join(styles)})")
    report: dict[str, object] = {
        "path": relative,
        "name": str(package.get("name") or package_root.name),
        "languages": languages,
        "styles": styles,
        "scripts": _scripts(package),
        "evidence": evidence,
    }
    for field, mapping in DEPENDENCY_GROUPS.items():
        report[field] = _matched(dependencies, mapping)
    return report


def _backend_markers(root: Path) -> list[str]:
    return sorted({label for filename, label in BACKEND_MARKERS.items() if (root / filename).is_file()})


def _root_project_name(root: Path, package_files: Iterable[Path]) -> str:
    root_package = root / "package.json"
    if root_package in package_files:
        package = _load_package(root_package)
        if package.get("name"):
            return str(package["name"])
    return root.name


def detect_project(target: Path) -> dict[str, object]:
    root = target.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"目标目录不存在或不可读：{root}")

    package_files = _package_files(root)
    packages = [_package_report(root, path) for path in package_files]
    root_package: dict[str, Any] = {}
    if (root / "package.json").is_file():
        root_package = _load_package(root / "package.json")
    has_workspaces = bool(root_package.get("workspaces"))
    if len(packages) > 1 or has_workspaces:
        shape = "monorepo"
    elif len(packages) == 1:
        shape = "single-package"
    else:
        shape = "repository"

    backend_markers = _backend_markers(root)
    pending_questions = [
        f"请确认 {package['name']} ({package['path']}) 使用的前端框架"
        for package in packages
        if not package["frameworks"]
    ]
    if not packages and not backend_markers:
        pending_questions.append("未识别到 package.json 或后端项目标记，请确认项目类型")

    return {
        "projectName": _root_project_name(root, package_files),
        "root": str(root),
        "shape": shape,
        "packages": packages,
        "backendMarkers": backend_markers,
        "pendingQuestions": pending_questions,
    }
