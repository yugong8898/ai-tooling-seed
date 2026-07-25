# 技术栈：<框架 + 构建>（<子项目定位>）

## 适用项目
- `<sub-project-A/>`（路径带完整前缀）
- `<sub-project-B/>`

## 框架与构建
- 框架：<React 18 / Vue 3 ...>
- 构建：<Vite / Webpack / Umi ...>
- 语言：TypeScript

## 样式方案
- <Less / Sass / CSS Modules>，命名 kebab-case

## 版本禁区（禁止升级/变更）
- <react-dom 16.x 勿升级 / Umi2 禁升 / SSR 顶层禁 window>

## ESLint 验证命令
```bash
cd <完整前缀>/<子项目> && npx eslint src --ext .ts,.tsx
```

## 请求封装
- <axios 实例路径 / 拦截器>

## i18n
- <vue-i18n / i18next>

---

**文档版本**: v1.0
**最后更新**: <YYYY年MM月>
**整理人**: <姓名>
