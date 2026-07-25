# AI 工具配置种子脚手架（ai-tooling-seed）

> 配套文档：本目录内的《项目技术栈文档体系搭建与维护手册》（**自包含标准，不依赖任何外部项目**）。
> 本目录是**可复制的初始骨架**，用于换设备后 / 新项目快速补齐 AI 工具配置（CodeBuddy / Qoder / Cursor 三工具）。

## 它解决什么
- **不依赖 `wlyd/`、`bondee/`、`yd/` 等任何具体项目**即可落地整套 AI 工具配置。
- 复制即用：内含通用技能、角色 prompt 骨架、项目规则模板、README/AGENTS 模板。
- 你只需填「项目专属事实」（技术栈、版本禁区、CDN 等），**禁止脑补**。

## 目录结构
```
ai-tooling-seed/
├── README.md                              # 本说明（换设备 onboarding 流程）
├── 项目技术栈文档体系搭建与维护手册.md     # 配套标准手册（自包含，本目录即种子）
├── .md/prompts/                           # 技术栈 + 角色 prompt 源（填内容）
│   ├── stack-index.md         # 索引模板
│   ├── stack-<type>.md        # 单类技术栈模板
│   └── role-*.md (11)         # 角色 prompt 骨架
├── templates/                 # 项目级骨架模板（含 <proj> 占位）
│   ├── AGENTS.md              # AI 协作指南模板（四张索引表）
│   └── PROJECT-README.md      # 项目总览模板
├── .codebuddy/                # 权威源
│   ├── rules/project-rules.template.md
│   ├── skills/ (7 个通用技能)
│   └── snippets/ (4 个模板：react/vue 组件、api、number 格式化，按框架增删)
├── .qoder/                    # 镜像 .codebuddy（rules + skills）
└── .cursor/                   # 镜像（rules/skills/snippets/context/settings/extensions）
```

## 换设备快速接收项目（六步）
1. **放骨架**：把本种子整体复制到目标项目根（或 `git clone` 后重命名为项目目录）。
2. **改名规则文件**：`.codebuddy/rules/project-rules.template.md` → `<proj>-project-rules.md`；`.qoder/rules/` 同。
3. **镜像技能/片段**（`.codebuddy/` 为权威源）：
   ```bash
   mkdir -p .qoder/skills .cursor/skills .cursor/snippets
   cp -r .codebuddy/skills/* .qoder/skills/
   cp -r .codebuddy/skills/* .cursor/skills/
   cp -r .codebuddy/snippets/* .cursor/snippets/
   ```
4. **填技术栈**（最关键，禁脑补）：编辑 `.md/prompts/stack-index.md` 与各 `stack-<type>.md`，先读各子项目 `package.json` 与 `*.less/*.scss/*.css` 核实框架/样式/版本禁区。
5. **填项目专属事实**：`role-*.md`、各 `SKILL.md` 里的 `<proj>` 占位与版本禁区、CDN 等，以实际代码为准。
6. **落地文档**：把 `templates/AGENTS.md`、`templates/PROJECT-README.md` 复制为项目根 `AGENTS.md`/`README.md` 并填真实信息；`.cursor/rules/ref-tech-stack.mdc` 为技术栈索引指针（与 `.md/prompts/stack-index.md` 对齐，落地时填真实技术栈）；`.cursor/` 整体复制（含 `rules/` 模块化规则、`settings.json`/`extensions.json`）。
7. **校验**：按手册第七章校验清单逐条核对（重点：rules/ 只放 project-rules.md，stack 不进 rules/）。

## 与 wlyd/ 等已有项目的关系
本种子**不依赖**任何外部项目。`wlyd/`/`bondee/`/`yd/` 若存在本地，仅作**可选对照示例**，非必需。所有标准以本目录内的《项目技术栈文档体系搭建与维护手册》为准。
