# Task-002: 认证工具层 — JWT + bcrypt

> **适合 AI 直接完成** ✅

## 任务名

实现 JWT 生成/验证 + 密码哈希/校验工具函数

## 目标

提供被认证接口（task-005）和中间件（task-004）调用的基础工具。

## 范围

- 创建 `backend/app/utils/auth.py`
  - `hash_password(password: str) -> str` — bcrypt 哈希
  - `verify_password(plain: str, hashed: str) -> bool` — bcrypt 校验
  - `create_token(user_id: int, username: str) -> str` — 生成 JWT
  - `decode_token(token: str) -> dict | None` — 验证并解析 JWT
- 更新 `backend/.env` 新增 `JWT_SECRET_KEY`
- 更新 `backend/app/config.py` 新增 `jwt_secret_key` 配置项
- 更新 `backend/requirements.txt` 新增 `PyJWT`、`bcrypt`

## 非目标

- 不写 API 接口
- 不写 Fernet 加密（task-003）
- 不写中间件（task-004）

## 输入

- `docs/data-contract.md` 第 6 节冻结项：JWT 算法 HS256、Payload 结构、有效期 7 天
- 现有 `backend/app/config.py`

## 输出

- `backend/app/utils/auth.py`
- 更新后的 `backend/app/config.py`
- 更新后的 `backend/.env`
- 更新后的 `backend/requirements.txt`

## 技术约束

- JWT 算法：HS256
- JWT Payload：`{"user_id": int, "username": str, "exp": int}`
- 有效期：7 天（`timedelta(days=7)`）
- 密码哈希：bcrypt，`bcrypt.gensalt()` 默认 rounds
- `.env` 中 `JWT_SECRET_KEY` 用 `openssl rand -hex 32` 生成，不硬编码
- 所有函数为纯函数/无状态，方便单元测试

## 依赖关系

- 前置：无
- 后续：task-004（中间件）、task-005（认证接口）依赖本任务

## 验收标准

- [ ] `create_token(1, "test")` 返回非空字符串
- [ ] `decode_token(valid_token)` 返回含 user_id/username/exp 的 dict
- [ ] `decode_token(expired_token)` 返回 None
- [ ] `decode_token("garbage")` 返回 None
- [ ] `verify_password("abc123", hash_password("abc123"))` 返回 True
- [ ] `verify_password("wrong", hash_password("abc123"))` 返回 False
- [ ] `docker compose build hongxin-api && docker compose up -d hongxin-api` 成功

## 建议执行顺序

1. 在容器外 `pip install PyJWT bcrypt` 或直接改 requirements.txt 后 rebuild
2. 用 `openssl rand -hex 32` 生成 JWT_SECRET_KEY，写入 `.env`
3. 在 `config.py` 中新增字段
4. 创建 `utils/auth.py`
5. 用 `docker exec hongxin-api python3 -c "..."` 逐个函数测试

## Progress

- [x] 2026-04-02 — 更新 requirements.txt（+PyJWT 2.8.0, bcrypt 4.1.2）+ rebuild
- [x] 2026-04-02 — 生成 JWT_SECRET_KEY 写入 .env
- [x] 2026-04-02 — config.py 新增 jwt_secret_key 字段
- [x] 2026-04-02 — 创建 utils/auth.py（4 个函数）
- [x] 2026-04-02 — Dockerfile 基础镜像换华为云镜像 + apt/pip 换阿里云源
- [x] 2026-04-02 — 容器内验证全部函数通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| D1 | Dockerfile 基础镜像换华为云镜像 | 原 Docker Hub 网络不稳定，构建失败 | 2026-04-02 |
| D2 | apt/pip 源换阿里云镜像 | 同上，加速国内构建 | 2026-04-02 |

## Surprises & Discoveries

## Handoff / Resume Notes

完成后告知 task-004/005 开发者：
- `create_token(user_id, username)` 和 `decode_token(token)` 已可用
- `hash_password` 和 `verify_password` 已可用
- `from app.utils.auth import create_token, decode_token, hash_password, verify_password`
