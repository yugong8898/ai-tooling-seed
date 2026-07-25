---
description: React + TypeScript 函数组件模板（<项目> 规范）
---
```tsx
import { FC } from 'react';

const <Comp>: FC = () => {
  return <div className="<comp>"><!-- ... --></div>;
};

export default <Comp>;
```
> 样式用 kebab-case className；以实际项目约定为准，禁止脑补专属工具。
