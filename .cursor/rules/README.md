# Cursor 规则结构

`.cursor/rules/` 是项目规则的唯一人工维护位置。

- `core-*.mdc`：每次对话加载的通用规则，必须包含 `alwaysApply: true`。
- `ref-*.mdc`：按描述加载的参考入口，不复制详细技术事实。
- `tech-*.mdc`：只有项目确实需要文件匹配规则时才创建。

运行 `python3 scripts/ai_tooling.py generate .` 后，CodeBuddy 与 Qoder 的单文件规则会从 `core-*.mdc` 按文件名字典序确定性生成。
