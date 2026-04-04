# Task-010: 设置页 — Cookie 配置

> **需要人工拍板交互细节** ⚠️

## 任务名

实现用户 Cookie 配置页面（保存 + 检测有效性）

## 目标

用户可以在这个页面填写自己的小红书 Cookie，并检测其是否有效。

## 范围

- 创建 `frontend/src/components/SettingsPage.vue`
  - Cookie 输入区域（textarea）
  - 「保存 Cookie」按钮
  - 「检测有效性」按钮
  - 状态展示：未配置 / 已配置（未检测） / 已配置（有效） / 已配置（已过期）
  - 使用说明：简要引导文案，告诉用户如何从小红书获取 Cookie
- 在 `App.vue` 中注册 `settings` 状态

## 非目标

- 不做 Cookie 自动抓取/刷新
- 不做多个 Cookie 管理
- 不做其他设置项

## 输入

- task-008 的 `authApi.saveCookie`、`authApi.checkCookie`、`getCurrentUser`
- task-006 的后端接口
- 现有项目 UI 风格

## 输出

- `frontend/src/components/SettingsPage.vue`
- 更新 `App.vue` 的 `currentStep` 类型增加 `'settings'`

## 技术约束

- textarea 宽度 100%，高度 6-8 行，placeholder 提示粘贴完整 Cookie
- 「保存 Cookie」按钮 → 调用 `authApi.saveCookie({cookies})` → 成功提示
- 「检测有效性」按钮 → 调用 `authApi.checkCookie()` → 显示结果
- 按钮在请求中显示 loading 状态，防止重复点击
- 页面顶部有返回按钮（回到首页）
- 未配置 Cookie 时显示引导文案：
  - "请按以下步骤获取小红书 Cookie："
  - "1. 打开 xiaohongshu.com 并登录"
  - "2. 按 F12 打开开发者工具"
  - "3. 切换到 Network 标签页，刷新页面"
  - "4. 找到任意请求，复制 Request Headers 中的 Cookie 完整内容"
  - "5. 粘贴到下方输入框中"

## 依赖关系

- 前置：task-006（后端 Cookie 接口）、task-008（前端 auth 工具）
- 后续：task-011（导航栏设置入口）、task-012（集成验收）

## 验收标准

- [ ] 页面正常渲染，有引导文案
- [ ] 粘贴 Cookie → 点保存 → 成功提示
- [ ] 空 Cookie → 点保存 → 错误提示
- [ ] 已保存 Cookie → 点「检测有效性」→ 显示有效/无效
- [ ] 未保存 Cookie → 点「检测有效性」→ 提示先保存
- [ ] 请求中按钮 loading，不可重复点击
- [ ] 返回按钮正常跳转首页

## 建议执行顺序

1. 创建 `SettingsPage.vue` 静态页面
2. 接入 saveCookie API
3. 接入 checkCookie API
4. 加 loading 状态和错误处理
5. 在 App.vue 中注册 settings 状态
6. 测试完整流程

## Progress

- [x] 2026-04-04 06:35 — 创建 SettingsPage.vue（Cookie 输入 + 引导文案 + 状态展示）
- [x] 2026-04-04 06:35 — 接入 saveCookie API
- [x] 2026-04-04 06:35 — 接入 checkCookie API
- [x] 2026-04-04 06:35 — 加 loading + 错误处理
- [x] 2026-04-04 06:35 — App.vue 替换占位为 SettingsPage 组件
- [x] 2026-04-04 06:35 — Docker 构建通过
- [x] 2026-04-04 06:35 — 验收通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| D1 | 使用卡片式布局（600px 居中） | 与 LoginPage 风格一致 | 2026-04-04 |
| D2 | onMounted 自动调用 getCookieStatus | 进入页面即显示当前 Cookie 配置状态 | 2026-04-04 |
| D3 | 状态分 4 种：none/saved/valid/invalid | 覆盖所有场景，用户一目了然 | 2026-04-04 |
| D4 | 保存后清空 textarea | 避免明文 Cookie 残留页面 | 2026-04-04 |

## Surprises & Discoveries

- App.vue 中 settings 状态已在 task-009 中注册，无需重复添加

## Handoff / Resume Notes

完成后告知 task-011 开发者：
- `SettingsPage.vue` 已完成
- App.vue 中 `currentStep` 已包含 `'settings'`
- 导航栏设置按钮跳转方式：`currentStep = 'settings'`
