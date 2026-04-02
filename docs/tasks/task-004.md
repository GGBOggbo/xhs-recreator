# Task-004: JWT 鉴权中间件 + 路由保护

> **适合 AI 直接完成** ✅

## 任务名

实现 JWT 校验依赖项，应用到所有需要鉴权的接口

## 目标

所有 `/api/*` 接口（白名单除外）必须携带有效 JWT，否则返回 401。

## 范围

- 创建 `backend/app/middleware/auth.py`
  - `get_current_user(token: str = Depends(oauth2_scheme)) -> dict` — FastAPI 依赖项
  - 解析 Token → 返回 `{"user_id": int, "username": str}`
  - 无效/过期 → 抛 HTTPException 401
- 改造 `backend/app/api/routes.py`
  - 所有路由函数加 `user = Depends(get_current_user)` 参数
  - 白名单：`/api/auth/*` 全部路径不需要鉴权

## 非目标

- 不写 auth 接口（task-005 做）
- 不处理 Token 黑名单
- 不做基于角色的权限区分

## 输入

- task-002 的 `decode_token` 函数
- 现有 `backend/app/api/routes.py`
- `docs/data-contract.md` 第 4.6 节

## 输出

- `backend/app/middleware/auth.py`
- 改造后的 `backend/app/api/routes.py`

## 技术约束

- 使用 FastAPI 的 `Depends()` 机制
- 使用 `fastapi.security.OAuth2PasswordBearer` 提取 Token
- tokenUrl 指向 `/api/auth/login`
- 白名单处理：auth 路由用单独的 `APIRouter`，不加鉴权依赖
- 校验成功后将 `user_id` 和 `username` 传递给路由函数
- 所有 401 返回统一格式：`{"detail": "未登录或登录已过期"}`

## 依赖关系

- 前置：task-002（JWT 工具函数）
- 后续：task-005、task-006、task-007 依赖本任务的鉴权机制

## 验收标准

- [ ] 无 Token 访问 `GET /api/fetch?url=...` → 返回 401
- [ ] 有效 Token 访问 `GET /api/fetch?url=...` → 正常通过（不会因鉴权报错）
- [ ] 过期 Token → 返回 401
- [ ] 无效 Token（乱字符串）→ 返回 401
- [ ] `POST /api/auth/register` 不需要 Token
- [ ] `POST /api/auth/login` 不需要 Token

## 建议执行顺序

1. 阅读 `routes.py`，了解现有路由结构
2. 创建 `middleware/auth.py`，实现 `get_current_user`
3. 在 `routes.py` 的每个路由函数加 `Depends(get_current_user)`
4. 确保 auth 路由（task-005 会创建）不受影响
5. curl 测试：无 Token → 401，有 Token → 通过

## Progress

- [ ] ____-__-__ __:__ — 阅读现有路由代码
- [ ] ____-__-__ __:__ — 创建 middleware/auth.py
- [ ] ____-__-__ __:__ — 改造 routes.py 加依赖注入
- [ ] ____-__-__ __:__ — curl 测试全部场景
- [ ] ____-__-__ __:__ — 验收通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| | | | |

## Surprises & Discoveries

## Handoff / Resume Notes

完成后告知后续 task 开发者：
- 所有 routes.py 中的路由已加鉴权，函数签名多了 `user = Depends(get_current_user)`
- `user` 是一个 dict：`{"user_id": int, "username": str}`
- 新增路由如需鉴权，同样加 `user = Depends(get_current_user)`
- auth 相关路由（/api/auth/*）在单独文件，不受影响
