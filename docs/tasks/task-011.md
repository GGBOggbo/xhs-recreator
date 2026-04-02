# Task-011: 导航栏改造 — 用户名 / 设置入口 / 注销

> **需要人工拍板布局** ⚠️

## 任务名

改造 App.vue 导航栏：显示当前用户名、设置入口、注销按钮

## 目标

导航栏展示登录状态，提供设置和注销入口。

## 范围

- 改造 `frontend/src/App.vue` 导航栏
  - 右侧区域：用户名显示 + 设置图标按钮 + 注销按钮
  - 设置按钮 → `currentStep = 'settings'`
  - 注销按钮 → 调用 `logout()` → 跳登录页
  - 夜间模式切换按钮保留
  - 帮助按钮和头像可暂时移除或保留
- 改造 `frontend/src/components/LandingPage.vue`（如需要）
  - 确保登录后才能进入落地页

## 非目标

- 不做用户头像上传
- 不做下拉菜单
- 不做个人中心页

## 输入

- task-008 的 `getCurrentUser`、`logout`
- 现有 `App.vue` 导航栏代码
- 现有夜间模式切换逻辑

## 输出

- 改造后的 `frontend/src/App.vue`

## 技术约束

- 用户名从 `getCurrentUser().username` 获取
- 注销：`logout()` 清 Token + `currentStep = 'login'`
- 设置按钮用齿轮图标（SVG inline）
- 注销按钮用退出图标（SVG inline）或文字「退出」
- 移动端：用户名可缩短（超过 6 字符截断），设置/注销用图标
- 暗色模式适配（`.dark-mode` CSS）

## 依赖关系

- 前置：task-008（auth 工具）、task-009（登录页，确保注销后跳转正确）
- 后续：task-012（集成验收）

## 验收标准

- [ ] 登录后导航栏右侧显示用户名
- [ ] 点击设置图标 → 进入设置页
- [ ] 点击注销 → 清除 Token → 跳转登录页
- [ ] 注销后导航栏无用户名、无设置/注销按钮
- [ ] 暗色模式下导航栏正常
- [ ] 移动端布局正常（不溢出）

## 建议执行顺序

1. 阅读 App.vue 现有导航栏代码
2. 在 `header-actions` 区域加用户名 + 设置按钮 + 注销按钮
3. 从 `getCurrentUser()` 读取用户名
4. 注销按钮绑定 `logout()`
5. 设置按钮绑定 `currentStep = 'settings'`
6. 暗色模式 CSS 适配
7. 移动端响应式调整

## Progress

- [ ] ____-__-__ __:__ — 阅读现有导航栏代码
- [ ] ____-__-__ __:__ — 添加用户名显示
- [ ] ____-__-__ __:__ — 添加设置按钮
- [ ] ____-__-__ __:__ — 添加注销按钮
- [ ] ____-__-__ __:__ — 暗色模式适配
- [ ] ____-__-__ __:__ — 移动端响应式
- [ ] ____-__-__ __:__ — 验收通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| | | | |

## Surprises & Discoveries

## Handoff / Resume Notes

完成后告知 task-012 开发者：
- 导航栏已完成改造
- 注销流程：logout() → currentStep='login'
- 设置入口：currentStep='settings'
