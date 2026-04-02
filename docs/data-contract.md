# 红薯创作坊 — Data & Contract Draft（MVP）

---

## 1. 核心数据模型

MVP 只涉及两张表及其关系：

```
users (1) ──── (N) tasks
```

一个用户可以有多个任务，一个任务只属于一个用户。

---

## 2. 关键字段定义

### 2.1 users 表

```sql
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role          VARCHAR(10) DEFAULT 'user',      -- 'admin' | 'user'
    xhs_cookies_encrypted TEXT,                     -- Fernet 加密后的 Cookie 明文
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, 自增 | 用户 ID |
| username | VARCHAR(20) | UNIQUE, NOT NULL | 登录名，3-20 字符 |
| password_hash | VARCHAR(128) | NOT NULL | bcrypt 哈希值 |
| role | VARCHAR(10) | DEFAULT 'user' | 角色，MVP 里 admin 与 user 行为一致 |
| xhs_cookies_encrypted | TEXT | NULLABLE | Fernet 加密的小红书 Cookie，未配置时为 NULL |
| created_at | TIMESTAMP | DEFAULT now | 注册时间 |

### 2.2 tasks 表（现有改造）

```sql
-- 已有字段不变，新增：
ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id);
```

| 新增字段 | 类型 | 约束 | 说明 |
|---------|------|------|------|
| user_id | INTEGER | FK → users(id) | 任务归属用户，已有数据设为 NULL |

---

## 3. 关键状态流转

### 3.1 用户 Cookie 状态

```
NULL（未配置）
       │
       ▼  PUT /api/auth/cookie
  encrypted_value（已配置）
       │
       ▼  POST /api/auth/cookie/check
  ┌────┴────┐
valid=true  valid=false
  （可用）    （已过期，需重新填写）
```

前端判断逻辑：
- 登录返回 `has_cookie: false` → 引导去设置页
- 登录返回 `has_cookie: true` → 正常使用
- 任务创建失败返回 Cookie 相关错误 → 提示去设置页更新

### 3.2 用户鉴权状态

```
未登录（无 Token）
    │
    ▼  POST /api/auth/register → 注册成功
    ▼  POST /api/auth/login → 返回 Token
已登录（有 Token）
    │
    ├─ Token 有效 → 正常访问
    ├─ Token 过期 → API 返回 401 → 前端跳登录页
    │
    ▼  前端清除 Token
已注销（无 Token）
```

---

## 4. API Contract

### 4.1 POST `/api/auth/register` — 注册

**Request:**
```json
{
  "username": "zhangsan",
  "password": "abc123"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "注册成功，请登录"
}
```

**Error 400:**
```json
{
  "detail": "用户名已存在"
}
```

**Error 422:**
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "ensure this value has at least 3 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

> 注：422 由 FastAPI 的 Pydantic 校验自动返回。

---

### 4.2 POST `/api/auth/login` — 登录

**Request:**
```json
{
  "username": "zhangsan",
  "password": "abc123"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 1,
      "username": "zhangsan",
      "role": "admin",
      "has_cookie": true
    }
  }
}
```

**Error 401:**
```json
{
  "detail": "用户名或密码错误"
}
```

---

### 4.3 GET `/api/auth/me` — 当前用户信息

**Request Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "zhangsan",
    "role": "admin",
    "has_cookie": true,
    "created_at": "2026-04-02T10:00:00"
  }
}
```

**Error 401:**
```json
{
  "detail": "未登录或登录已过期"
}
```

---

### 4.4 PUT `/api/auth/cookie` — 保存 Cookie

**Request Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Request:**
```json
{
  "cookies": "a1=xxx; webId=xxx; web_session=xxx; ..."
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Cookie 保存成功"
}
```

**Error 400:**
```json
{
  "detail": "Cookie 不能为空"
}
```

---

### 4.5 POST `/api/auth/cookie/check` — 检测 Cookie 有效性

**Request Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Request:** 无 request body（使用当前用户已保存的 Cookie）

**Response 200（有效）:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "message": "Cookie 有效"
  }
}
```

**Response 200（无效）:**
```json
{
  "success": true,
  "data": {
    "valid": false,
    "message": "Cookie 已过期，请重新获取"
  }
}
```

**Error 400（未配置）:**
```json
{
  "detail": "未配置 Cookie，请先保存后再检测"
}
```

---

### 4.6 现有接口改造约定

**所有需要鉴权的接口（除 register/login 外）：**

Request Header 必须带：
```
Authorization: Bearer <token>
```

缺少或过期 → 返回 401：
```json
{
  "detail": "未登录或登录已过期"
}
```

**创建任务改造（POST `/api/task`）：**
- 后端从 Token 解析 `user_id`，自动写入 task
- 前端无需传 `user_id`

**查询历史改造（GET `/api/history`）：**
- 后端按当前 `user_id` 过滤，只返回当前用户的任务

**爬取笔记改造（GET `/api/fetch`）：**
- 后端读取当前用户的 Cookie
- 用户未配置 Cookie → 返回：
```json
{
  "detail": "请先在小红书 Cookie 设置中配置您的 Cookie"
}
```

---

## 5. 异常与错误返回约定

### HTTP 状态码

| 状态码 | 含义 | 场景 |
|--------|------|------|
| 200 | 成功 | 所有正常响应 |
| 400 | 业务错误 | 参数校验失败、Cookie 为空、用户名已存在 |
| 401 | 未认证 | 缺少 Token、Token 过期、Token 无效 |
| 404 | 不存在 | 任务 ID 不存在或非当前用户的任务 |
| 422 | 参数格式错误 | Pydantic 自动校验（字段缺失、类型错误） |
| 500 | 服务端错误 | 未知异常 |

### 错误响应格式（统一）

```json
{
  "detail": "人类可读的错误描述"
}
```

### 前端处理规则

| 状态码 | 前端行为 |
|--------|---------|
| 401 | 清除 localStorage Token，跳转登录页 |
| 400 | 弹出 `detail` 提示信息 |
| 404 | 弹出「未找到」提示 |
| 500 | 弹出「服务异常，请稍后重试」 |

---

## 6. 冻结与可变约定

### 必须冻结（开发前锁定，开发中不改）

| 项 | 值 | 理由 |
|----|---|------|
| users 表结构 | 如上定义 | 所有接口依赖此结构 |
| JWT 签名算法 | HS256 | 选定后不能中途换 |
| JWT Payload 结构 | `{"user_id": int, "username": str, "exp": int}` | 前后端共同依赖 |
| JWT 有效期 | 7 天 | 短了体验差，长了不安全，7 天是平衡点 |
| Token Header 格式 | `Authorization: Bearer <token>` | HTTP 标准约定 |
| 错误响应格式 | `{"detail": "..."}` | 与 FastAPI 默认格式一致 |
| Cookie 加密方式 | Fernet 对称加密 | 选定后更换会导致已有数据失效 |
| `.env` 密钥字段 | `JWT_SECRET_KEY`、`COOKIE_ENCRYPTION_KEY` | 部署时生成，不变 |

### 允许后续微调

| 项 | 当前值 | 微调范围 |
|----|--------|---------|
| 用户名长度限制 | 3-20 字符 | 可放宽到 2-30 |
| 密码最小长度 | 6 位 | 可提高到 8 位 |
| Cookie 检测的具体 API 调用 | 调用一次 get_note_info | 可换成更轻量的接口 |
| 登录页 UI 样式 | 待设计 | 不影响数据契约 |
| `has_cookie` 字段名 | has_cookie | 可改为 `cookie_configured`，但前后端需同步 |
