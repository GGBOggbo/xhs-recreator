# Task-003: 加密工具层 — Fernet

> **适合 AI 直接完成** ✅

## 任务名

实现 Cookie 加密存储的加解密工具

## 目标

提供被 Cookie 管理接口（task-006）调用的 Fernet 对称加密工具。

## 范围

- 创建 `backend/app/utils/crypto.py`
  - `encrypt_cookie(plaintext: str) -> str` — Fernet 加密，返回 base64 字符串
  - `decrypt_cookie(encrypted: str) -> str` — Fernet 解密，返回明文
- 更新 `backend/.env` 新增 `COOKIE_ENCRYPTION_KEY`
- 更新 `backend/app/config.py` 新增 `cookie_encryption_key` 配置项
- 更新 `backend/requirements.txt` 新增 `cryptography`

## 非目标

- 不写 API 接口
- 不处理密钥轮换逻辑

## 输入

- `docs/data-contract.md` 第 2.1 节（xhs_cookies_encrypted 字段）
- 现有 `backend/app/config.py`

## 输出

- `backend/app/utils/crypto.py`
- 更新后的 `backend/app/config.py`
- 更新后的 `backend/.env`
- 更新后的 `backend/requirements.txt`

## 技术约束

- 使用 `cryptography.fernet.Fernet`
- 密钥由 `.env` 的 `COOKIE_ENCRYPTION_KEY` 读取
- 密钥生成方式：`Fernet.generate_key().decode()`，写入 `.env` 后不再更换
- 加密结果存 TEXT 字段（base64 字符串）
- 函数为纯函数，无副作用

## 依赖关系

- 前置：无（可与 task-002 并行）
- 后续：task-006（Cookie 管理接口）依赖本任务

## 验收标准

- [ ] `encrypt_cookie("hello")` 返回非空字符串（base64）
- [ ] `decrypt_cookie(encrypt_cookie("hello"))` 返回 `"hello"`
- [ ] 空 Cookie 明文 → `encrypt_cookie("")` 不报错
- [ ] 错误密钥解密 → 抛出异常（`InvalidToken`）
- [ ] `docker compose build hongxin-api && docker compose up -d hongxin-api` 成功

## 建议执行顺序

1. `pip install cryptography` 或改 requirements.txt
2. 生成密钥：`python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` 写入 `.env`
3. `config.py` 新增字段
4. 创建 `utils/crypto.py`
5. 容器内验证

## Progress

- [ ] ____-__-__ __:__ — 更新 requirements.txt + rebuild
- [ ] ____-__-__ __:__ — 生成密钥写入 .env
- [ ] ____-__-__ __:__ — config.py 新增字段
- [ ] ____-__-__ __:__ — 创建 utils/crypto.py
- [ ] ____-__-__ __:__ — 容器内验证
- [ ] ____-__-__ __:__ — 验收通过

## Decision Log

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| | | | |

## Surprises & Discoveries

## Handoff / Resume Notes

完成后告知 task-006 开发者：
- `encrypt_cookie(plaintext)` 和 `decrypt_cookie(encrypted)` 已可用
- `from app.utils.crypto import encrypt_cookie, decrypt_cookie`
- Cookie 存入数据库前调 encrypt，取出后调 decrypt
