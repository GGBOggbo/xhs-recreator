# Task-006: Cookie 管理接口

> **适合 AI 直接完成** ✅

## 任务名

实现用户 Cookie 的保存、状态查询、有效性检测接口

## 目标

用户可以保存自己的小红书 Cookie，并检测其是否有效。

## 范围

- 在 `backend/app/api/auth.py` 中新增接口：
  - `GET /api/auth/cookie` — 查询 Cookie 状态（已配置/未配置）
  - `PUT /api/auth/cookie` — 保存/更新 Cookie（加密存储）
  - `POST /api/auth/cookie/check` — 检测当前 Cookie 有效性

## 非目标

- 不做 Cookie 明文读取接口（不返回明文给前端）
- 不做 Cookie 历史记录
- 不做自动刷新 Cookie

## 输入

- `docs/data-contract.md` 第 4.4 ~ 4.5 节
- task-003 的 `encrypt_cookie`、`decrypt_cookie`
- task-005 的 auth 路由结构
- task-004 的 `get_current_user` 依赖项

## 输出

- 更新后的 `backend/app/api/auth.py`

## 技术约束

- 三个接口都需要鉴权（`Depends(get_current_user)`）
- PUT 接口：
  - Request body：`{"cookies": "a1=xxx; web_session=xxx; ..."}`
  - cookies 字段不能为空字符串 → 400 `"Cookie 不能为空"`
  - 调用 `encrypt_cookie()` 加密后存入 `users.xhs_cookies_encrypted`
- GET 接口：
  - 返回 `{"success": true, "data": {"has_cookie": true/false}}`
  - 不返回明文 Cookie
- Check 接口：
  - 从数据库读用户的 `xhs_cookies_encrypted` → decrypt
  - 未配置 → 400 `"未配置 Cookie，请先保存后再检测"`
  - 已配置 → 调用一次 `spider.get_note_info`（用一个测试笔记 URL）验证
  - 成功 → `{"valid": true, "message": "Cookie 有效"}`
  - 失败（登录过期等）→ `{"valid": false, "message": "Cookie 已过期，请重新获取"}`

## 依赖关系

- 前置：task-003（加密）、task-004（鉴权）、task-005（auth 路由）
- 后续：task-008（前端 Cookie 配置页）依赖本任务

## 验收标准

- [ ] `PUT /api/auth/cookie`（带 Token + 有效 Cookie）→ 200
- [ ] `PUT /api/auth/cookie`（空字符串）→ 400
- [ ] `PUT /api/auth/cookie`（不带 Token）→ 401
- [ ] 数据库中存储的是加密密文，不是明文
- [ ] `GET /api/auth/cookie`（已配置）→ `has_cookie: true`
- [ ] `GET /api/auth/cookie`（未配置）→ `has_cookie: false`
- [ ] `POST /api/auth/cookie/check`（有效 Cookie）→ `valid: true`
- [ ] `POST /api/auth/cookie/check`（过期 Cookie）→ `valid: false`
- [ ] `POST /api/auth/cookie/check`（未配置）→ 400

## 建议执行顺序

1. 阅读 task-005 产出的 `auth.py`，了解路由结构
2. 定义 Pydantic 模型（`CookieRequest`）
3. 实现 GET /cookie
4. 实现 PUT /cookie
5. 实现 POST /cookie/check
6. curl 逐个测试

## Progress

- [ ] ____-__-__ __:__ — 定义 Pydantic 模型
- [ ] ____-__-__ __:__ — 实现 GET /cookie
- [ ] ____-__-__ __:__ — 实现 PUT /cookie
- [ ] ____-__-__ __:__ — 实现 POST /cookie/check
- [ ] ____-__-__ __:__ — curl 测试
- [ ] ____-__-__ __:__ — 验收通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| | | | |

## Surprises & Discoveries

## Handoff / Resume Notes

完成后告知 task-007 开发者：
- Cookie 检测接口路径：`POST /api/auth/cookie/check`
- Spider 需要的 Cookie 明文可通过 `decrypt_cookie(user.xhs_cookies_encrypted)` 获取
- 未配置 Cookie 的用户：`xhs_cookies_encrypted is None`
