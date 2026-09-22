---
description: API 请求方法模板（axios 风格）
---
```ts
import request from '@/utils/request';

export function <apiName>(params: <Req>) {
  return request.get('<path>', { params });
}
```
> 注：`request` 实例路径以实际项目为准，禁止脑补。
