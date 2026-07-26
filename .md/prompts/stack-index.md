# <项目名> 项目技术栈索引（stack-index）

根据文件路径归属的子项目，找到对应技术栈文件，再引用该文件获取完整规范。

> ⚠️ **重要**：本仓库<统一使用 <Less/SCSS/CSS> / 同时使用 Sass 与 Less，按子项目而定>，切勿跨子项目混用样式。具体分用规则在各子项目行「样式方案」列与各 `stack-*.md`「样式方案」段。

## 项目 → 技术栈文件

| 子项目 | 技术栈文件 | UI 库 | 样式方案 | 特殊规范 |
|--------|-----------|-------|---------|---------|
| `<sub-project-A/>` | [stack-<type1>.md](stack-<type1>.md) | <antd/element/...> | <Less/SCSS/CSS> | <如：React X 勿升级；SSR 禁顶层 window> |
| `<sub-project-B/>` | [stack-<type2>.md](stack-<type2>.md) | ... | ... | ... |
| `<sub-project-C/>` | [stack-<type1>.md](stack-<type1>.md) | ... | ... | <与 A 同栈可共用一份> |

> 每行一个子项目；同栈子项目可指向同一份 stack 文件。技术栈文件复制 `stack-<type>.md` 改名填写。

## 速查：状态管理方案
| 子项目 | 状态管理 |
|--------|---------|
| `<sub-project-A/>` | <Redux / Redux+Saga / dva / 无全局状态（组件本地 state）/ 后端 service 分层> |
| `<sub-project-B/>` | ... |

## 速查：金额 / 数字格式化真实工具（禁止自造通用函数）
| 子项目 | 真实工具 |
|--------|---------|
| `<sub-project-A/>` | `src/utils/<文件>` → `<函数名>`（<用途>） |
| `<sub-project-B/>` | `src/utils/<文件>` → `<函数名>` |

## 速查：版本禁区（禁止升级 / 变更）
- <React X 勿升 Y；webpack X 勿升 5；Umi X 勿升 Y；antd X 勿升 Y；Taro X 勿升 Y；RN X 勿升 Y+>
- node-sass 勿换 dart-sass；`<子项目X>` 用 `<Less>`，其余 `<SCSS>`，严格分用勿混

## 排除目录（非活跃项目，勿纳入改动）
> 列出被排除的快照/旧版/杂物目录及原因，例如：`<crm-20190929/>`（<子项目> 历史快照）、`<rnP/>`（旧版）、`<xxx/>`（散落资料）。

---

**填写指引**：
1. 复制 `stack-<type>.md` 为具体 `stack-<栈名>.md`，逐段填实际事实（以 package.json、真实 src 结构为准，禁止脑补）。
2. 本索引表与各 stack 文件保持「子项目 → 栈 → 样式 → 版本禁区 → 金额工具」一致。
3. 任何 stack 事实变更，须同步更新本索引速查表。

**文档版本**: v1.0
**最后更新**: <YYYY年MM月>
**整理人**: <姓名>
