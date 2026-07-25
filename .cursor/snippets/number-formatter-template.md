---
description: 数字格式化模板
---
```ts
export function formatNumber(value: number): string {
  return value.toLocaleString('zh-CN');
}
```
> 注：区域/精度以项目实际为准，不照搬其它项目实现。
