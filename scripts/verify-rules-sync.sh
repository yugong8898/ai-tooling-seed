#!/usr/bin/env bash
#
# verify-rules-sync.sh —— 校验某项目的「三工具规则」是否保持同步
#
# 单一事实源（SSOT）：.codebuddy/rules/<proj>-project-rules.md
# 镜像/桥接副本：     .qoder/rules/<proj>-project-rules.md
# Cursor 端承载：      .cursor/rules/core-project-rules.mdc     （短索引/短指针，须 alwaysApply: true）
#                     .cursor/rules/core-ai-collaboration.mdc  （AI 协作与独立判断，正文须与 SSOT AI 章节一致）
#
# 用法:
#   bash verify-rules-sync.sh [项目根目录]      # 默认校验当前目录
#   bash verify-rules-sync.sh ../wlyd           # 校验指定项目
#
# 退出码:
#   0 = 三端同步一致
#   1 = 存在不一致（.codebuddy 与 .qoder 内容不同 / 缺文件 / frontmatter 缺失 / cursor 端 AI 协作不一致）
#
# 建议接 git pre-commit hook：漂移直接阻断提交。

set -u

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"
name="$(basename "$ROOT")"

CB="$ROOT/.codebuddy/rules/$name-project-rules.md"
QO="$ROOT/.qoder/rules/$name-project-rules.md"
CU="$ROOT/.cursor/rules/core-project-rules.mdc"
AIC="$ROOT/.cursor/rules/core-ai-collaboration.mdc"

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

echo "-- 2) frontmatter 校验（codebuddy/qoder/cursor 均需 alwaysApply: true）--"
check_frontmatter "$CB"
check_frontmatter "$QO"
check_frontmatter "$CU"

echo "-- 3) Cursor 端承载校验 --"
if [ -f "$CU" ]; then
  cu_lines=$(wc -l < "$CU" | tr -d ' ')
  if [ "$cu_lines" -gt 200 ]; then
    echo "  [警告] $CU 行数=$cu_lines，疑似退化为全量副本（应保持短索引/短指针，<200 行）"
  fi
else
  echo "  [缺失] $CU"
  fail=1
fi

if [ ! -f "$AIC" ]; then
  echo "  [缺失] $AIC（AI 协作规则独立承载文件）"
  fail=1
else
  if ! head -3 "$AIC" | grep -q "alwaysApply: true"; then
    echo "  [frontmatter] $AIC 缺少 'alwaysApply: true'"
    fail=1
  fi
  ssot_body="$(python3 - "$CB" <<'PY'
import sys
p=sys.argv[1]
txt=open(p,encoding='utf-8').read().split('\n')
start=None
for i,l in enumerate(txt):
    if l.startswith('## ') and 'AI 协作' in l:
        start=i; break
if start is None:
    print(''); sys.exit(0)
end=len(txt)
for j in range(start+1,len(txt)):
    if txt[j].startswith('## ') and j!=start:
        end=j; break
body='\n'.join(txt[start:end]).rstrip()
while body.endswith('---'):
    body=body[:-3].rstrip()
print(body)
PY
)"
  mdc_body="$(python3 - "$AIC" <<'PY'
import sys
p=sys.argv[1]
txt=open(p,encoding='utf-8').read().split('\n')
if txt and txt[0].strip()=='---':
    for k in range(1,len(txt)):
        if txt[k].strip()=='---':
            txt=txt[k+1:]; break
body='\n'.join(txt).strip()
while body.endswith('---'):
    body=body[:-3].rstrip()
print(body)
PY
)"
  if [ "$ssot_body" = "$mdc_body" ]; then
    echo "  [OK] core-ai-collaboration.mdc ≡ SSOT AI 协作章节"
  else
    echo "  [不一致] core-ai-collaboration.mdc 与 SSOT AI 协作章节内容不同，需同步"
    fail=1
  fi
fi

if [ "$fail" -eq 0 ]; then
  echo "== 通过：三工具规则同步一致 =="
  exit 0
else
  echo "== 失败：存在不一致，请按《维护手册》原则 12 同步后重试 =="
  exit 1
fi
