---
name: commit-helper
description: 生成符合规范的 Commit 信息。触发："生成提交信息"、"帮我提交"、"写个 commit"
---

# commit-helper（提交信息生成）

## 触发场景
- 根据 diff 生成 Conventional Commits 信息
- 拆分过大多文件提交

## 工作流程
1. 读取 `git diff` / `git status`
2. 归并相关改动为语义化提交
3. 输出 type(scope): subject + body

## 注意事项
- 遵循本仓库提交规范（见 `<proj>-project-rules.md`）
- 关联需求/缺陷单号
