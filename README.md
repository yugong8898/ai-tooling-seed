# AI Tooling Seed v2

一个前端优先、零第三方依赖的 AI 项目配置脚手架。它先读取目标仓库中的真实配置，再安全合并 `.cursor/` 权威源，并生成 CodeBuddy、Qoder 和兼容 Prompt 文件。

## 环境要求

- Python 3.9 或更高版本
- Git（仅用于正常项目维护，CLI 不会自动提交或推送）

## 快速开始

```bash
# 1. 只读识别项目
python3 scripts/ai_tooling.py detect /path/to/project

# 2. 预览全部文件操作，不写入
python3 scripts/ai_tooling.py init /path/to/project --dry-run

# 3. 初始化并自动合并
python3 scripts/ai_tooling.py init /path/to/project

# 4. 修改 .cursor 后刷新兼容文件
python3 scripts/ai_tooling.py generate /path/to/project

# 5. 校验完整性
python3 scripts/ai_tooling.py verify /path/to/project
```

默认使用 `frontend` profile。非前端仓库可传入 `--profile generic`，只安装通用协作能力。

## 安全模型

- `detect` 和 `verify` 始终只读。
- `init --dry-run` 展示 `CREATE / MERGE / UPDATE / UNCHANGED / CONFLICT`，不写文件。
- 正式写入前，已有文件备份到 `.ai-tooling/backups/UTC时间/`。
- README 与 AGENTS 只更新受控区块，区块外内容保持不变。
- Cursor JSON 配置按键合并，目标项目已有值优先。
- 无法安全识别的同名文件不会被覆盖。
- 重复执行 `init` 是幂等的。

## 权威源与生成物

只编辑 `.cursor/`：

```text
.cursor/
├── ai-tooling.json     # 项目识别结果、profile、策略
├── rules/              # 模块化规则
├── prompts/            # 技术栈与角色 Prompt
├── skills/             # 可复用技能
├── snippets/           # 代码片段
├── context/            # 项目知识
├── settings.json
└── extensions.json
```

运行 `generate` 后生成：

- `.codebuddy/`
- `.qoder/`
- `.md/prompts/`

生成文件带有明确标记，直接修改会被 `verify` 报告为漂移。

## 项目识别范围

当前重点识别 React、Vue、Vite、Next.js、Umi、uni-app、Taro、Webpack、TypeScript、常见 UI/状态库和 CSS/Less/Sass。Python、Go、Java、Rust 只记录轻量项目标记，不生成重型后端规则。

CLI 不推断 CDN、接口字段、业务约定、金额工具或依赖禁升规则；这些事实需要代码、正式文档或用户确认作为证据。

## 开发与测试

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ai_tooling.py verify .
bash scripts/verify-rules-sync.sh .
```

架构设计和实施计划位于 `docs/superpowers/`，旧项目实践与历史事故记录位于 `docs/legacy/`。

<!-- ai-tooling:start -->
## 本仓库 AI 工具配置

本仓库以 `.cursor/` 为唯一人工维护源，其他工具目录由生成器维护。
<!-- ai-tooling:end -->
