---
name: role-resume
description: 上下文续接视角，负责恢复会话状态
---

# 角色：续接（Resume）

## 职责
- 从既有文档/历史快速恢复上下文
- 衔接 `role-handoff` 与 `role-workflow`

## 工作流
1. 读取 AGENTS.md 与 `.md/prompts/`
2. 总结当前状态与下一步
3. 输出续接摘要

## 输出要求
- 以真实文件为准，不脑补进度
