# AI Tooling Seed 开发指南

本仓库实现一个 Python 标准库 CLI。修改行为时先增加失败测试，再做最小实现；完成前运行完整测试与项目自校验。

## 关键边界

- `.cursor/` 是同步内容的唯一人工维护源。
- `.codebuddy/`、`.qoder/` 和 `.md/prompts/` 是生成物，不直接编辑。
- 不覆盖目标项目无法识别的同名文件。
- 不把项目探测中的猜测写成事实。
- 保持 Python 3.9 兼容，不增加第三方运行时依赖。

## 验证命令

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ai_tooling.py generate .
python3 scripts/ai_tooling.py verify .
git diff --check
```

<!-- ai-tooling:start -->
## AI 工具协作入口

开始工作前读取 `.cursor/ai-tooling.json` 与 `.cursor/rules/`；生成目录不得直接编辑。
<!-- ai-tooling:end -->
