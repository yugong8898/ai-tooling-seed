---
name: memory-update
description: 将已验证且长期有效的项目知识沉淀到 Cursor 权威源
---

# Memory Update

1. 只提取由代码、正式文档、运行结果或用户确认支持的稳定事实。
2. 技术栈写入 `.cursor/prompts/stack-*.md`；协作规则写入 `.cursor/rules/`；业务知识写入 `.cursor/context/`。
3. 避免在多个源文件重复同一事实，给出证据路径与更新时间。
4. 修改后运行 `generate` 和 `verify`，不直接编辑生成目录。
5. 临时需求、猜测、聊天草稿和敏感信息不进入长期记忆。
