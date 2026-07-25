---
name: requirement-change-analysis
description: 需求/变更影响分析。触发："分析需求"、"评估改动影响"、"这个改动涉及哪些"
---

# requirement-change-analysis（需求/变更分析）

## 触发场景
- 需求拆解与评估
- 变更影响范围分析

## 工作流程
1. 明确需求目标与边界
2. 结合 `code-analyzer` 评估影响文件
3. 输出任务拆解 + 风险（含版本禁区）

## 注意事项
- 与 `role-pm` 协作界定范围
- 结论基于真实代码与 `.md/prompts/stack-*`
