# Task-009: 登录 / 注册页面

> **需要人工拍板 UI/交互细节** ⚠️

## 任务名

实现登录/注册二合一页面 + App.vue 登录状态集成

## 目标

未登录用户看到登录/注册页面，登录成功后进入首页。

## 范围

- 创建 `frontend/src/components/LoginPage.vue`
  - 登录表单：用户名 + 密码 + 登录按钮
  - 注册表单：用户名 + 密码 + 确认密码 + 注册按钮
  - 登录/注册 Tab 切换或链接切换
  - 表单验证（前端）
  - 错误提示展示
- 改造 `frontend/src/App.vue`
  - 新增 `currentStep = 'login'` 状态
  - 登录状态下渲染 `LoginPage`
  - 登录成功后跳转 `landing`（如未配 Cookie 则跳 `settings`）
  - 刷新页面时检查 localStorage Token，有则恢复登录态
  - LandingPage 组件不再作为默认首页，需登录后才可见

## 非目标

- 不做忘记密码
- 不做第三方登录
- 不做记住我（Token 已有 7 天有效期）

## 输入

- task-008 的 `authApi.register`、`authApi.login`、`isAuthenticated`、`login`、`logout`
- 现有 `App.vue` 的 `currentStep` 状态管理
- 现有项目 CSS 风格

## 输出

- `frontend/src/components/LoginPage.vue`
- 改造后的 `frontend/src/App.vue`

## 技术约束

- Vue 3 `<script setup lang="ts">`
- 与现有页面风格一致（参考 `PreviewConfig.vue` 的表单风格）
- 用户名 3-20 字符，密码最少 6 位（前端校验 + 后端 Pydantic 也会校验）
- 注册成功 → 提示「注册成功，请登录」→ 自动切换到登录 Tab
- 登录成功 → 检查 `has_cookie`：
  - true → 跳转 `landing`
  - false → 跳转 `settings`（引导配置 Cookie）
- 已登录状态刷新页面 → 从 localStorage 恢复 Token → 不跳登录页
- `onMounted` 中检查 `isAuthenticated()`，已登录直接跳首页

## 依赖关系

- 前置：task-008（前端 auth 工具）
- 后续：task-012（集成验收）

## 验收标准

- [ ] 打开页面 → 看到登录页
- [ ] 切换到注册 Tab → 填写 → 注册成功 → 提示 → 自动切回登录 Tab
- [ ] 输入已注册的用户名密码 → 登录成功 → 跳转首页
- [ ] 用户名/密码为空 → 按钮禁用或前端提示
- [ ] 服务端错误（用户名已存在/密码错误）→ 页面显示错误信息
- [ ] 已登录状态刷新页面 → 停留在首页，不跳登录
- [ ] 首次登录未配 Cookie → 跳转设置页

## 建议执行顺序

1. 阅读 `App.vue`，理解 `currentStep` 状态管理
2. 创建 `LoginPage.vue`（先做静态页面）
3. 接入 `authApi.register` / `authApi.login`
4. 改造 `App.vue`：加 login 状态、onMounted 检查登录态
5. 测试完整流程：注册 → 登录 → 首页 → 刷新不跳登录

## Progress

- [x] 2026-04-04 04:20 — 创建 LoginPage.vue 静态页面（登录/注册 Tab + 表单验证）
- [x] 2026-04-04 04:20 — 接入注册 API（authApi.register）
- [x] 2026-04-04 04:20 — 接入登录 API（authApi.login + authLogin）
- [x] 2026-04-04 04:25 — 改造 App.vue login 状态（currentStep 增加 'login'|'settings'）
- [x] 2026-04-04 04:25 — 登录态恢复逻辑（onMounted 检查 isAuthenticated）
- [x] 2026-04-04 04:33 — Docker 构建通过，前端编译成功
- [x] 2026-04-04 04:33 — 验收通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| D1 | 登录页使用 Tab 切换而非链接切换 | Tab 更直观，符合主流登录页设计 | 2026-04-04 |
| D2 | 登录成功后 emit `login-success` 而非直接跳转 | 让 App.vue 控制跳转逻辑，组件职责更清晰 | 2026-04-04 |
| D3 | 登录页不显示顶部导航栏（header v-if !== login） | 未登录时不需要导航，简化体验 | 2026-04-04 |
| D4 | settings 页先做占位 | task-010 才实现设置页，先给占位可点击进入首页 | 2026-04-04 |

## Surprises & Discoveries

- 登录页 min-height 用 `calc(100vh - 72px)` 不准确（登录页无 header），改为 `100vh`

## Handoff / Resume Notes

完成后告知 task-010/011 开发者：
- `LoginPage.vue` 已完成
- `App.vue` 已新增 `login` 状态
- 登录成功后 `has_cookie=false` 会跳 `settings`
- 所有 `currentStep` 类型已更新为包含 `'login'` 和 `'settings'`
