# Cursor 规则结构（ai-tooling-seed 模板）

## 说明

本目录为 Cursor 模块化规则（`.mdc`），由原来单文件 `.cursorrules` 重构而来。

- **旧形态**：根目录单文件 `.cursorrules`（仅内联技术栈索引 + 指针）
- **新形态**：`.cursor/rules/*.mdc`（带 frontmatter，按 `core-/tech-/ref-` 分类）
- ⚠️ 根目录 `.cursorrules` 已废弃（若从旧单文件迁移，原文件备份为根目录 `.cursorrules.backup`）

## 规则结构（模板，含 `<proj>` / `<项目名>` 占位，落地时替换）

```
.cursor/rules/
├── core-general-standards.mdc   ✅ 通用规范（始终应用）
├── core-project-rules.mdc       ✅ 项目规则指针（始终应用）
├── core-ai-collaboration.mdc    ✅ AI 协作与独立判断（始终应用，正文与 SSOT 一致）
└── ref-tech-stack.mdc           ✅ 技术栈索引指针（智能应用）
```

**规则应用模式**：
- **始终应用**（`core-` 前缀，`alwaysApply: true`）：每次对话自动生效
- **智能应用**（`ref-` 前缀，`description`）：AI 按上下文判断加载

> 因本种子为通用模板，技术栈/规范细节统一指向 `.md/prompts/stack-*.md` 与 `.codebuddy/rules/<proj>-project-rules.md`，故 `.cursor/rules/` 下只放「指针 + 通用规范」，不重复技术栈事实。

## 落地方式

复制本种子时，`.cursor/` 整体复制到目标项目根（含本 `rules/`），再将 `<proj>` / `<项目名>` 占位替换为真实项目名即可。无需再复制根 `.cursorrules`。

**整理时间**：2026年7月25日
**整理人**：王新骏
