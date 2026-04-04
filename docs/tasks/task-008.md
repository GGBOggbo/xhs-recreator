# Task-008: 前端认证基础设施

> **适合 AI 直接完成** ✅

## 任务名

实现前端 Token 管理 + axios 拦截器 + API 封装

## 目标

全局认证状态管理，所有请求自动带 Token，401 自动跳登录。

## 范围

- 创建 `frontend/src/utils/auth.ts`
  - `getToken(): string | null` — 从 localStorage 读 Token
  - `setToken(token: string): void` — 存 Token
  - `removeToken(): void` — 清 Token
  - `isAuthenticated(): boolean` — 是否已登录
  - `getCurrentUser(): object | null` — 从 localStorage 读用户信息
  - `login(token, user): void` — 存 Token + 用户信息
  - `logout(): void` — 清除所有，跳登录页
- 创建 axios 实例（或改造现有）
  - 请求拦截器：自动加 `Authorization: Bearer <token>`
  - 响应拦截器：401 → 清 Token → `window.location` 跳登录
- 统一 API 封装
  - `authApi.register(data)` → POST `/api/auth/register`
  - `authApi.login(data)` → POST `/api/auth/login`
  - `authApi.getMe()` → GET `/api/auth/me`
  - `authApi.saveCookie(data)` → PUT `/api/auth/cookie`
  - `authApi.checkCookie()` → POST `/api/auth/cookie/check`
  - `authApi.getCookieStatus()` → GET `/api/auth/cookie`

## 非目标

- 不写页面组件
- 不改 App.vue
- 不做 Token 刷新逻辑

## 输入

- `docs/data-contract.md` API Contract 全部接口
- 现有前端代码中的 API 调用方式（可能有 axios 实例或 fetch）

## 输出

- `frontend/src/utils/auth.ts`

## 技术约束

- localStorage key：`xhs_token`（Token）、`xhs_user`（用户信息 JSON）
- TypeScript，与现有项目一致
- 使用 `axios` 库（项目已有依赖则直接用，没有则安装）
- 401 跳转目标：`/` 根路径（App.vue 会根据无 Token 状态显示登录页）
- 不用 vue-router（项目无路由库，用 `window.location` 或状态管理）

## 依赖关系

- 前置：无（可与后端 task 并行）
- 后续：task-009（登录页）、task-010（设置页）、task-011（导航栏）依赖本任务

## 验收标准

- [ ] `login(token, user)` 后 `getToken()` 返回 token
- [ ] `isAuthenticated()` 返回 true
- [ ] `logout()` 后 `getToken()` 返回 null
- [ ] axios 请求自动携带 Authorization header
- [ ] 模拟 401 响应 → Token 被清除

## 建议执行顺序

1. 阅读现有前端代码中的 API 调用方式
2. 创建 `utils/auth.ts`，实现 Token 管理函数
3. 创建/改造 axios 实例，加拦截器
4. 封装 auth API 调用函数
5. 确认现有组件（LinkInput、PreviewConfig 等）的 API 调用能无缝切换到新 axios 实例

## Progress

- [x] 2026-04-04 — 阅读现有 API 调用方式（4 组件直接 import axios）
- [x] 2026-04-04 — 实现 Token 管理函数（getToken/setToken/login/logout 等）
- [x] 2026-04-04 — 创建 axios 拦截器（请求自动带 Token，401 自动清 Token）
- [x] 2026-04-04 — 封装 auth API（register/login/getMe/saveCookie/checkCookie/getCookieStatus）
- [x] 2026-04-04 — 确认现有组件兼容（api 导出可直接替换现有 import axios）
- [x] 2026-04-04 — 验收通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| D1 | authApi.register/login 用原始 axios 而非 api 实例 | 注册登录不需要 Token | 2026-04-04 |
| D2 | 401 拦截直接 reload 而非跳转 | 无 vue-router，reload 后 App.vue 检查无 Token 显示登录页 | 2026-04-04 |
| D3 | 不修改现有组件的 import | 仅提供 api 导出，后续 task-009~011 逐步迁移 | 2026-04-04 |

## Surprises & Discoveries

## Handoff / Resume Notes

完成后告知 task-009/010/011 开发者：
- `import { login, logout, getToken, isAuthenticated, getCurrentUser } from '../utils/auth'`
- `import { authApi, api } from '../utils/auth'` — authApi 是认证相关，api 是通用带 Token 的 axios
- 所有后端请求用 `api` 实例，不要用原生 axios 或 fetch
