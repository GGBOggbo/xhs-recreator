# Task-005: 认证接口 — 注册 / 登录 / Me

> **适合 AI 直接完成** ✅

## 任务名

实现用户注册、登录、获取当前信息三个接口

## 目标

提供用户身份创建和验证的 API 入口。

## 范围

- 创建 `backend/app/api/auth.py`（独立路由文件）
  - `POST /api/auth/register` — 注册
  - `POST /api/auth/login` — 登录
  - `GET /api/auth/me` — 获取当前用户信息
- 在 `backend/app/main.py` 中注册 auth 路由
- 定义 Pydantic 请求/响应模型（放在 auth.py 或单独 models 文件中）

## 非目标

- 不做 Cookie 管理接口（task-006）
- 不做用户管理 CRUD
- 不做密码修改/重置

## 输入

- `docs/data-contract.md` 第 4.1 ~ 4.3 节（API Contract）
- task-001 的 `User` 模型
- task-002 的 `hash_password`、`verify_password`、`create_token`、`decode_token`

## 输出

- `backend/app/api/auth.py`
- 更新后的 `backend/app/main.py`

## 技术约束

- Pydantic 模型：`RegisterRequest(username, password)`、`LoginRequest(username, password)`
- username: 3-20 字符（Pydantic `Field(min_length=3, max_length=20)`）
- password: 最少 6 位（Pydantic `Field(min_length=6)`）
- 注册逻辑：
  - 查 username 是否已存在 → 400 `"用户名已存在"`
  - 判断 users 表是否为空 → 第一个用户 role = 'admin'
  - hash_password → 存库
- 登录逻辑：
  - 查 username → 不存在 → 401 `"用户名或密码错误"`
  - verify_password → 不匹配 → 401 `"用户名或密码错误"`
  - create_token → 返回 Token + 用户信息
  - `has_cookie` = `user.xhs_cookies_encrypted is not None`
- Me 接口：依赖 task-004 的 `get_current_user`
- 路由前缀：`/api/auth`
- 使用 `APIRouter(prefix="/api/auth", tags=["auth"])`
- **本文件的路由不经过 task-004 的鉴权中间件**（白名单）

## 依赖关系

- 前置：task-001（User 模型）、task-002（JWT + bcrypt 工具）
- 可与 task-004 并行开发（但集成测试需 task-004 完成）
- 后续：task-006（Cookie 接口也写在 auth.py 中）

## 验收标准

- [ ] `POST /api/auth/register {"username":"test","password":"123456"}` → 200 成功
- [ ] 重复注册同一用户名 → 400 `"用户名已存在"`
- [ ] 用户名 < 3 字符 → 422
- [ ] 密码 < 6 位 → 422
- [ ] 第一个注册用户 → `role: "admin"`
- [ ] 第二个注册用户 → `role: "user"`
- [ ] `POST /api/auth/login {"username":"test","password":"123456"}` → 200 返回 Token
- [ ] 登录返回含 `has_cookie: false`（未配置 Cookie）
- [ ] 密码错误 → 401 `"用户名或密码错误"`
- [ ] 不存在的用户名 → 401
- [ ] `GET /api/auth/me`（带 Token）→ 200 返回用户信息
- [ ] `GET /api/auth/me`（不带 Token）→ 401

## 建议执行顺序

1. 在 auth.py 中定义 Pydantic 模型
2. 实现 register 接口
3. 实现 login 接口
4. 实现 me 接口（暂不用 Depends，先用 Header 手动解析 Token）
5. 在 main.py 中注册路由
6. 逐个 curl 测试
7. 集成 task-004 的 Depends 后再测一轮

## Progress

- [x] 2026-04-04 — 定义 Pydantic 模型（RegisterRequest, LoginRequest）
- [x] 2026-04-04 — 实现 register（含首个用户自动 admin）
- [x] 2026-04-04 — 实现 login（含 has_cookie 字段）
- [x] 2026-04-04 — 实现 me（依赖 get_current_user）
- [x] 2026-04-04 — 注册路由到 main.py（auth_router 优先于 api_router）
- [x] 2026-04-04 — curl 测试全部 12 项验收标准通过
- [x] 2026-04-04 — 验收通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| D1 | auth_router 注册在 api_router 之前 | 确保 /api/auth/* 优先匹配 | 2026-04-04 |
| D2 | 无 Token 时返回 OAuth2 默认 "Not authenticated" | 缺少 Token vs 过期 Token 分开处理 | 2026-04-04 |
| D3 | _get_db 复用 routes.py 的 SessionLocal | 避免重复创建 engine | 2026-04-04 |

## Surprises & Discoveries

## Handoff / Resume Notes

完成后告知 task-006 开发者：
- `auth.py` 已创建，路由前缀 `/api/auth`
- Cookie 管理接口直接追加到 `auth.py` 中
- `from app.api.auth import router as auth_router` 已在 main.py 注册
- `has_cookie` 字段已包含在 login 和 me 的返回中
