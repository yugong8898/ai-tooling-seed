#!/usr/bin/env bash
#
# verify-rules-sync.sh —— 校验某项目的「三工具规则」是否保持同步
#
# 单一事实源（SSOT）：.codebuddy/rules/<proj>-project-rules.md
# 镜像/桥接副本：     .qoder/rules/<proj>-project-rules.md
#                    .cursor/rules/core-project-rules.mdc
#
# 用法:
#   bash verify-rules-sync.sh [项目根目录]      # 默认校验当前目录
#   bash verify-rules-sync.sh ../wlyd           # 校验指定项目
#
# 退出码:
#   0 = 三端同步一致
#   1 = 存在不一致（.codebuddy 与 .qoder 内容不同 / 缺文件 / frontmatter 缺失）
#
# 建议接 git pre-commit hook：漂移直接阻断提交。

set -u

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"
name="$(basename "$ROOT")"

CB="$ROOT/.codebuddy/rules/$name-project-rules.md"
QO="$ROOT/.qoder/rules/$name-project-rules.md"
CU="$ROOT/.cursor/rules/core-project-rules.mdc"

fail=0

check_frontmatter() {
  local f="$1"
  if [ ! -f "$f" ]; then
    echo "  [缺失] $f"
    fail=1
    return
  fi
  if ! head -3 "$f" | grep -q "alwaysApply: true"; then
    echo "  [frontmatter] $f 缺少 'alwaysApply: true'"
    fail=1
  fi
}

echo "== 校验项目: $name ($ROOT) =="

echo "-- 1) .codebuddy 与 .qoder 必须字节一致 --"
if [ ! -f "$CB" ]; then echo "  [缺失] $CB"; fail=1; fi
if [ ! -f "$QO" ]; then echo "  [缺失] $QO"; fail=1; fi
if [ -f "$CB" ] && [ -f "$QO" ]; then
  if diff -q "$CB" "$QO" >/dev/null 2>&1; then
    echo "  [OK] .codebuddy ≡ .qoder"
  else
    echo "  [不一致] .codebuddy 与 .qoder 的 project-rules.md 内容不同，需同步"
    fail=1
  fi
fi

echo "-- 2) frontmatter 校验（三端均需 alwaysApply: true）--"
check_frontmatter "$CB"
check_frontmatter "$QO"
check_frontmatter "$CU"

if [ "$fail" -eq 0 ]; then
  echo "== 通过：三工具规则同步一致 =="
  exit 0
else
  echo "== 失败：存在不一致，请按《维护手册》原则 12 同步后重试 =="
  exit 1
fi
