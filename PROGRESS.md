# PROGRESS.md — XHS ReCreator Development Status

> Last updated: 2026-04-02

## Current Phase

**Login System MVP** — Phase 3: Frontend Infrastructure（进行中）

## Task Status

### Phase 1: Backend Infrastructure

| Task | Name | Status | Notes |
|------|------|--------|-------|
| [task-001](docs/tasks/task-001.md) | 数据模型 + DB 迁移 | ✅ Done | users 表已创建，tasks 已加 user_id |
| [task-002](docs/tasks/task-002.md) | JWT + bcrypt 工具 | ✅ Done | 4 函数验证通过，Dockerfile 换国内镜像源 |
| [task-003](docs/tasks/task-003.md) | Fernet 加密工具 | ✅ Done | encrypt/decrypt_cookie 验证通过 |
| [task-004](docs/tasks/task-004.md) | JWT 中间件 + 路由保护 | ✅ Done | 7 个路由全部加鉴权，curl 验证通过 |

### Phase 2: Backend Business

| Task | Name | Status | Notes |
|------|------|--------|-------|
| [task-005](docs/tasks/task-005.md) | 注册/登录/Me 接口 | ✅ Done | 3 接口 + 12 项验收全通过 |
| [task-006](docs/tasks/task-006.md) | Cookie 管理接口 | ✅ Done | GET/PUT/POST cookie，9 项验收通过 |
| [task-007](docs/tasks/task-007.md) | 任务用户绑定 | ✅ Done | 7 项验收全通过，用户隔离生效 |

### Phase 3: Frontend Infrastructure

| Task | Name | Status | Notes |
|------|------|--------|-------|
| [task-008](docs/tasks/task-008.md) | 前端 auth 基础 | ✅ Done | Token 管理 + 拦截器 + authApi |

### Phase 4: Frontend Pages

| Task | Name | Status | Notes |
|------|------|--------|-------|
| [task-009](docs/tasks/task-009.md) | 登录/注册页 | ⬜ Not started | 需拍板 UI |
| [task-010](docs/tasks/task-010.md) | 设置页 | ⬜ Not started | 需拍板交互 |
| [task-011](docs/tasks/task-011.md) | 导航栏改造 | ⬜ Not started | 需拍板布局 |

### Phase 5: Integration

| Task | Name | Status | Notes |
|------|------|--------|-------|
| [task-012](docs/tasks/task-012.md) | 集成验收 | ⬜ Not started | 人工操作 |

## Next Steps

1. **Start task-001, task-002, task-003 in parallel** (no dependencies between them)
2. Then task-004 → task-005 → task-006 + task-007
3. task-008 can start anytime (independent of backend)
4. task-009 → task-010 → task-011 (sequential, need UI approval)
5. task-012 final verification

## Completed Work (Pre-Login)

| Date | What | Commit |
|------|------|--------|
| 2026-03-28 | Architecture refactoring (CrawlerProvider + steps.py) | |
| 2026-03-28 | Landing page integration + Tailwind CSS v4 | |
| 2026-03-29 | Multi-style image generation (notebook/whiteboard) | |
| 2026-03-29 | Style selector in frontend | |
| 2026-03-30 | Spider_XHS URL parsing fix (xsec_token) | |

## Blockers & Risks

| # | Risk | Status |
|---|------|--------|
| R1 | Open registration vs internal deployment | ⚠️ Accepted for MVP |
| R2 | JWT no-blacklist logout | ⚠️ Accepted for MVP |
| R3 | SQLite concurrency | ✅ OK for small team |
| R4 | Fernet key rotation invalidates all cookies | ⚠️ Document only |
