---
name: commit-helper
description: 根据真实 Git diff 生成或执行语义清晰的提交；用户明确要求提交时使用
---

# Commit Helper

1. 读取 `git status`、暂存与未暂存 diff，识别用户原有改动。
2. 按可独立回滚和审查的行为边界建议拆分，不按文件数量机械拆分。
3. 生成 `type(scope): subject`，正文解释原因、行为变化与验证。
4. 不包含密钥、临时文件、构建产物或无关改动。
5. 只有用户明确要求执行提交时才运行 `git commit`，提交后重新检查状态。
