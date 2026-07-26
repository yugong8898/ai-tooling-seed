# <项目名> 项目开发协作指南

## 项目概览

<项目名> 是一个 <领域> 项目，采用 **monorepo** 方式组织多个子项目，同时使用 Cursor、Qoder、CodeBuddy 协同维护。

## 子项目

> 各子项目技术栈细节见 `.md/prompts/stack-index.md`（索引表），其按子项目指向对应 `stack-*.md` 详述文件。**本仓库<统一使用 Less / 同时使用 Sass 与 Less，按子项目而定，切勿跨项目混用 / 不使用 Sass/SCSS>**。
>
> 项目规则在 `.codebuddy/rules/<proj>-project-rules.md`、`.qoder/rules/<proj>-project-rules.md`、`.cursor/rules/*.mdc`（模块化）三处一致生效；技术栈详述**只在 `.md/prompts/` 单源**（不进 `rules/`），改技术栈后同步 `.cursor/rules/ref-tech-stack.mdc` 指针即可。

| 子项目 | 说明 | 技术栈（摘要） |
|--------|------|----------------|
| `<sub-A/>` | <职责> | <React X · TypeScript · Less（antd · Umi 4）> |
| `<sub-B/>` | <职责> | <Vue3 · TypeScript · Sass（Element Plus · Vite）> |

## 仓库结构

```
<proj>/
├── <sub-A>/                # <职责>
├── .md/                    # 技术栈 + 角色 prompt（唯一可编辑源）
│   └── prompts/            # stack-index + stack-* + role-*
├── .codebuddy/             # rules / skills / context / snippets（权威源）
├── .qoder/                 # rules / skills
├── .cursor/                # rules（*.mdc 模块化）/ skills / snippets / context / settings
└── AGENTS.md               # 本文档
```

## 开发规范

### 语言与沟通
- 文档与沟通统一使用**中文**；代码注释使用中文；Git commit 信息使用中文。

### 代码提交规范
- 无明确命令时不做任何代码提交操作；只在用户明确要求时才生成 commit 信息。
- Commit 格式详见 `.cursor/rules/core-general-standards.mdc` 相关节。

### 技术栈规范（摘要）
- <按 `stack-*.md` 摘录：框架、函数组件+Hooks / `<script setup>`、样式 kebab-case、CSS 属性顺序等>
- ⚠️ <版本禁区，如 react-dom 16.x 勿升级 / Umi2 禁升 / SSR 顶层禁 window / Sass 与 Less 按子项目分用勿混>

## 快速开始

各子项目为相互独立的工程，进入对应目录后按各自 `package.json` 的脚本启动。

```bash
cd <sub-A> && npm install && npm run dev
```

## Skills 索引

> **技能命名前缀规则（本手册基准）**：通用技能（`bugfix-helper` / `code-analyzer` / `commit-helper` / `memory-update`）**不加 `<proj>-` 前缀**；仅**项目专属技能**加前缀（如 `<proj>-review` / `<proj>-workflow` / `<proj>-requirement-change-analysis`）。下方列出全部 **7 个**技能，与「Prompts 角色索引」保持同步。

| Skill | 说明 | 触发场景 |
|-------|------|---------|
| `workflow` | 全链路研发流程编排器 | "走流程"、"继续上次进度" |
| `review` | 代码审查 | "帮我 review"、"检查改动" |
| `commit-helper` | Commit 信息生成 | "生成提交信息"、"帮我提交" |
| `code-analyzer` | 代码分析器（三种模式） | "分析影响范围"、"读懂这个模块" |
| `requirement-change-analysis` | 需求/变更分析 | "分析需求"、"评估改动影响" |
| `bugfix-helper` | 线上问题排查 | "排查这个问题"、"线上有个 bug" |
| `memory-update` | 记忆整理器 | "整理 memory"、"更新规则" |

> 凡角色引用了某 Skill，此处必须列出；凡本表增删某 Skill，须同步更新「Prompts 角色索引」表。`commit-helper` / `code-analyzer` / `memory-update` 等 Skill 仅以 Skill 形式存在、无对应角色 prompt，属正常。

## Snippets 模板

| 模板 | 说明 |
|------|------|
| `react-component-template` | React + TypeScript 函数组件模板 |
| `vue-component-template` | Vue 3 `<script setup>` 组件模板 |
| `api-method-template` | <项目> API 接口封装模板 |
| `number-formatter-template` | 数字格式化模板（按需） |

> 模板按项目实际框架增删：Vue 项目须补 `vue-component-template`；无数字格式化需求可省略 `number-formatter-template`。

## Prompts 角色索引（`.md/prompts/`）

手动多 Chat 场景使用，直接 `@.md/prompts/role-xxx.md` 激活。与对应 Skill 编排逻辑一致，修改一处需同步另一处。

**技术栈唯一索引**：`.md/prompts/stack-index.md`。所有角色 prompt 内联技术栈均已改为引用它，修改技术栈只需改这一处。

| 角色文件 | 说明 | 对应 Skill | 触发场景 |
|---------|------|-----------|---------|
| `role-workflow.md` | 全链路研发流程编排器（Prompt 版） | `workflow` | `@role-workflow.md 走流程` |
| `role-pm.md` | 需求分析师 | `requirement-change-analysis` | `@role-pm.md 分析需求` |
| `role-architect.md` | 架构师（技术方案设计） | - | `@role-architect.md 出方案` |
| `role-coder.md` | 开发工程师（逐文件编码） | - | `@role-coder.md 改 xxx.tsx` |
| `role-reviewer.md` | 代码审查员 | `review` | `@role-reviewer.md 审查改动` |
| `role-qa-checklist.md` | 提测清单生成器 | - | `@role-qa-checklist.md 提测` |
| `role-bugdetective.md` | Bug 侦探（根因定位） | `bugfix-helper` | `@role-bugdetective.md 排查 bug` |
| `role-ui-reviewer.md` | UI 还原审查员 | - | `@role-ui-reviewer.md 对比设计稿` |
| `role-refactor.md` | 重构师 | - | `@role-refactor.md 分析 xxx.tsx` |
| `role-resume.md` | 恢复续接员 | - | `@role-resume.md 恢复现场` |
| `role-handoff.md` | 中断交接员 | - | `@role-handoff.md 生成交接文档` |

## 上下文参考文档（Context，按需）

位于 `.codebuddy/context/`（Cursor 同步至 `.cursor/context/`），编码前可 `@` 引用快速获取背景知识：

| 文件 | 说明 |
|------|------|
| `known-pitfalls.md` | 已知坑点汇总（stack 之外的真实坑），编码前检索 |
| `business-terms.md` | 业务术语表与子项目职责 |
| `api-patterns.md` | 接口调用约定（stack 未覆盖的项目特有约定） |

## 配置维护说明

本项目配置文件同步规则：
- **主配置**：`.cursor/rules/*.mdc`（Cursor 模块化规则）+ `.cursor/`（skills / snippets / context / settings）
- **同步配置**：
  - `.codebuddy/rules/` - CodeBuddy 规则（与 `.md/prompts/` 同步）
  - `.codebuddy/skills/` - CodeBuddy 技能（权威源）
  - `.codebuddy/snippets/` - CodeBuddy 代码片段
  - `.codebuddy/context/` - 业务上下文（按需）
  - `.qoder/rules/`、`.qoder/skills/` - Qoder 同步
- 修改主配置时以 Cursor 侧为准，并同步更新其他工具配置；新增/下线 Skill、Snippet、角色或 Context 文件时，须同步更新本页对应索引表。

## AI 执行纪律标识（用户校验锚点，铁律）

> **本区块是用户校验「AI 是否按 AGENTS 与项目规则执行」的唯一锚点。**
> AI 每次处理涉及代码 / 文档 / skill / rules 修改的任务，**必须在回复末尾输出本标识**；用户凭标识是否齐全，判断本次是否走了规范流程。

**AI 每次动手前必做**：
1. 读取并遵循本 `AGENTS.md` 与 `.codebuddy/rules/<proj>-project-rules.md`（含 AI 协作、独立判断、接单确认、横向搜索、完成自检等）。
2. 涉及 skill / rules / context / snippets 改动，遵循「三端镜像同步」原则，不得只改一端。
3. 凡涉及数值计算，以脚本为重算/校验唯一来源，禁止手算另立公式。
4. 每次回复**开头以「<开头称呼探针，如 honey 王>」起句**、**末尾含「<结尾称呼探针，如 wang 工>」称呼**（双探针，见下），作为 AGENTS / rules 加载校验。

**双称呼探针（加载校验，强制）**：
- 回复**开头**必须以「<开头称呼探针，如 honey 王>」称呼起句 → 证明 `AGENTS.md` 已加载。
- 回复**末尾**须含「<结尾称呼探针，如 wang 工>」称呼（由 rules 文件约束，紧邻【规则对齐】之前一行）→ 证明 `rules` 已加载。
- 用户重置上下文后据此判断：两称呼齐全 = 双边约束均生效；只见开头称呼、不见结尾称呼 = rules 未生效；只见结尾称呼、不见开头称呼 = AGENTS 未生效。

> **占位替换指引**：复制骨架后，把 `<开头称呼探针>`/`<结尾称呼探针>` 替换为你实际使用的**两个不同**称呼。`<开头称呼探针>` 由本 `AGENTS.md` 约束；`<结尾称呼探针>` 须与三端 rules（`.codebuddy/` `.qoder/` `.cursor/rules/core-general-standards.mdc`）的「称呼探针」逐字一致。

**AI 每次交付前必输出（置于回复末尾）**：
```
【规则对齐】AGENTS✓  rules✓  横向搜索✓  三端同步✓  完成自检✅/⚠️
```
- 任一项缺 `✓` → 视为未走规范流程，用户应要求重做。
- 完成自检为 `⚠️` 时，必须先修正再交付，不得带问题交付。
- 此标识缺失 → 视为本次未遵循 AGENTS，用户可直接指出。

---

**文档版本**: v1.0
**最后更新**: <YYYY年MM月>
**整理人**: <姓名>
