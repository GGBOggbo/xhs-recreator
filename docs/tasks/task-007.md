# Task-007: 任务用户绑定 — Spider Cookie 读取 + 查询过滤

> **适合 AI 直接完成** ✅

## 任务名

改造现有业务代码：任务绑定用户、爬虫读用户 Cookie、历史按用户过滤

## 目标

让现有的二创流程在用户体系下正常运行。

## 范围

- 改造 `backend/app/api/routes.py`：
  - `POST /api/task` → 从 `get_current_user` 取 user_id 写入任务
  - `GET /api/history` → 按 user_id 过滤
  - `GET /api/task/{id}` → 校验 user_id 归属，非本人返回 404
  - `GET /api/fetch` → 读当前用户 Cookie，未配置返回 400
- 改造 `backend/app/services/spider.py`：
  - `fetch_note(url, cookies)` → cookies 参数由调用方传入
- 改造 `backend/app/services/task_runner.py`：
  - 运行任务时从用户 Cookie 解密后传给 spider
- 改造 `backend/app/api/routes.py` 的 `run_task_background`：
  - 启动后台任务时传入用户的 Cookie 明文

## 非目标

- 不改 Spider_XHS 第三方库代码
- 不改数据库表结构（task-001 已完成）
- 不改前端代码

## 输入

- task-004 的 `get_current_user` 依赖项
- task-003 的 `decrypt_cookie`
- task-006 的 Cookie 管理接口（了解 Cookie 存取逻辑）
- 现有 `routes.py`、`spider.py`、`task_runner.py`

## 输出

- 改造后的 `backend/app/api/routes.py`
- 改造后的 `backend/app/services/spider.py`（如需改动）
- 改造后的 `backend/app/services/task_runner.py`（如需改动）

## 技术约束

- `get_current_user` 返回 `{"user_id": int, "username": str}`
- Cookie 读取链路：`users.xhs_cookies_encrypted` → `decrypt_cookie()` → 明文 → 传给 spider
- 未配置 Cookie 时 `GET /api/fetch` 返回 400：`{"detail": "请先在小红书 Cookie 设置中配置您的 Cookie"}`
- 未配置 Cookie 时 `POST /api/task` 同样返回 400
- `GET /api/history` 加 WHERE `user_id = current_user_id`
- `GET /api/task/{id}` 加 WHERE `user_id = current_user_id`，找不到返回 404（不是 403，不暴露存在性）
- 后台任务（BackgroundTasks）需要把解密后的 Cookie 明文传过去，不能在后台线程中再查库解密（SQLite 不支持跨线程）

## 依赖关系

- 前置：task-001、task-003、task-004、task-005
- 后续：task-009（前端页面）依赖本任务

## 验收标准

- [ ] 用户 A 登录后创建任务 → tasks 表记录的 user_id = A 的 id
- [ ] 用户 B 登录后 GET /api/history → 看不到用户 A 的任务
- [ ] 用户 A 登录后 GET /api/task/{B的任务id} → 返回 404
- [ ] 用户已配置 Cookie → GET /api/fetch 正常爬取
- [ ] 用户未配置 Cookie → GET /api/fetch 返回 400 提示
- [ ] 用户已配置 Cookie → POST /api/task 后台任务正常执行
- [ ] 已有旧任务（user_id=NULL）不报错，登录后看不到

## 建议执行顺序

1. 阅读 `routes.py`、`spider.py`、`task_runner.py` 完整代码
2. 在 `routes.py` 所有路由加 `user = Depends(get_current_user)`（task-004 可能已做）
3. 改造 `/api/fetch`：读用户 Cookie → 未配置报 400 → 有配置传给 spider
4. 改造 `/api/task`：写入 user_id + 传用户 Cookie 给后台任务
5. 改造 `/api/history`：按 user_id 过滤
6. 改造 `/api/task/{id}`：校验归属
7. 多用户场景测试

## Progress

- [x] 2026-04-04 — 阅读现有代码（routes.py, task_runner.py, spider.py）
- [x] 2026-04-04 — 改造 /api/fetch — 读用户 Cookie，未配置返回 400
- [x] 2026-04-04 — 改造 /api/task — 写 user_id + 传 Cookie 明文给后台
- [x] 2026-04-04 — 改造 /api/history — 按 user_id 过滤（旧 user_id=NULL 任务不出现）
- [x] 2026-04-04 — 改造 /api/task/{id} + delete — 校验 user_id 归属
- [x] 2026-04-04 — 改造 task_runner + steps — cookies 参数传递链路
- [x] 2026-04-04 — 多用户场景测试全部 7 项验收标准通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| D1 | Cookie 明文在后台任务入口解密传入 | SQLite 不支持跨线程，后台不能再查库 | 2026-04-04 |
| D2 | user_id=NULL 旧任务对所有用户不可见 | 安全考虑，不暴露历史数据 | 2026-04-04 |
| D3 | 归属校验失败返回 404 非 403 | 不暴露任务存在性 | 2026-04-04 |

## Surprises & Discoveries

## Handoff / Resume Notes

完成后告知前端 task 开发者：
- 所有 `/api/*` 接口已需要 Token
- 未配置 Cookie 时返回 400 `"请先在小红书 Cookie 设置中配置您的 Cookie"`
- 用户隔离已生效，前端无需额外处理
