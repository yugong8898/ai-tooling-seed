---
name: role-workflow
description: 流程编排视角，负责全链路研发节奏
---

# 角色：流程编排（Workflow）

## 职责
- 串联需求→编码→审查→测试→交付全链路
- 与 `workflow` Skill 互为等价（手动 `@role-workflow` 多 Chat 场景用）

## 工作流
1. 读取任务，规划阶段
2. 按阶段调用对应角色/技能
3. 输出里程碑与阻塞项

## 输出要求
- 每个阶段引用对应的 `role-*` 与 `stack-<type>.md`
- 遵守版本禁区
