# Task-001: 数据模型 + 数据库迁移

> **适合 AI 直接完成** ✅

## 任务名

创建 User 模型 + tasks 表增加 user_id

## 目标

建立用户系统的数据基础：新增 `users` 表，改造 `tasks` 表。

## 范围

- 创建 `backend/app/models/user.py`（User ORM 模型）
- 改造 `backend/app/models/task.py`（新增 `user_id` 字段）
- 在 `backend/app/models/__init__.py` 或 `database.py` 中注册新模型
- 编写并执行数据库迁移（手动 ALTER TABLE）

## 非目标

- 不写 API 接口
- 不写前端代码
- 不处理用户关联逻辑（后续 task 做）

## 输入

- `docs/data-contract.md` 第 2 节的字段定义
- 现有 `backend/app/models/task.py`
- 现有 `backend/app/database.py`

## 输出

- `backend/app/models/user.py`
- 改造后的 `backend/app/models/task.py`
- 迁移后的 SQLite 数据库文件（`data/history.db`）

## 技术约束

- ORM：SQLAlchemy（现有）
- 数据库：SQLite（现有）
- `users` 表结构严格按照 data-contract 第 2.1 节
- `tasks.user_id` 为 INTEGER，允许 NULL（已有数据不受影响）
- `password_hash` 字段长度 VARCHAR(128)，为 bcrypt 留空间
- 确保 `User` 模型在 app 启动时被 import，Base.metadata.create_all 能建表

## 依赖关系

- 无前置依赖
- 后续 task-002 ~ task-007 均依赖本任务

## 验收标准

- [ ] `users` 表存在，字段/类型/约束符合 data-contract
- [ ] `tasks` 表新增 `user_id` 列，已有记录该列为 NULL
- [ ] `docker compose restart hongxin-api` 后服务正常启动，无报错
- [ ] 可通过 `sqlite3 data/history.db ".schema users"` 查看建表语句

## 建议执行顺序

1. 阅读 `backend/app/models/task.py` 和 `backend/app/database.py`，了解现有模型模式
2. 创建 `user.py`，保持与 task.py 一致的代码风格
3. 改造 `task.py`，加 `user_id` 字段 + 外键
4. 确保 user model 被 import（在 main.py 或 database.py 中注册）
5. 重启服务让 SQLAlchemy 自动建 users 表
6. 手动执行 `ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id);`
7. 验证

## Progress

- [x] 2026-04-02 15:05 — 阅读现有模型代码
- [x] 2026-04-02 15:08 — 创建 user.py
- [x] 2026-04-02 15:09 — 改造 task.py（加 user_id + ForeignKey）
- [x] 2026-04-02 15:10 — 注册模型到 __init__.py
- [x] 2026-04-02 15:14 — 重建 Docker 镜像 + 启动 → users 表自动创建
- [x] 2026-04-02 15:15 — 手动 ALTER TABLE tasks ADD user_id → 14 条已有数据 user_id=NULL
- [x] 2026-04-02 15:16 — 验收通过（health check OK，schema 正确）

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| D1 | User model 放在独立文件 user.py 而非加在 task.py | 职责分离，后续 auth 接口 import 更清晰 | 2026-04-02 |
| D2 | user_id 允许 NULL 不设 NOT NULL | 已有 14 条任务无归属，设 NOT NULL 会破坏数据 | 2026-04-02 |

## Surprises & Discoveries

- `Base = declarative_base()` 定义在 task.py 中，user.py 需要 `from app.models.task import Base` 来共享同一个 Base 实例。这不是理想的设计（Base 应该在独立的 base.py 中），但改动超出 task-001 范围，后续可优化。
- Docker 容器代码在 build 时 COPY 进去的，修改本地代码后必须 `docker compose build` + `docker compose up -d`，仅 restart 不会更新代码。

## Handoff / Resume Notes

完成后告知下一个 task（task-002）的开发者：
- users 表已创建，结构确认无误
- tasks 表已加 user_id，已有数据不受影响
- 数据库文件路径：`data/history.db`
