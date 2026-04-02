# API Reference — XHS ReCreator

## Base URL

```
http://localhost:8000/api
```

## Authentication

Most endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

Exceptions: `/api/auth/register`, `/api/auth/login`

---

## Auth Endpoints

### POST /api/auth/register

Register a new user.

**Request:**
```json
{ "username": "zhangsan", "password": "abc123" }
```

**Response 200:**
```json
{ "success": true, "message": "注册成功，请登录" }
```

**Errors:** 400 (username exists), 422 (validation)

---

### POST /api/auth/login

Login and get JWT token.

**Request:**
```json
{ "username": "zhangsan", "password": "abc123" }
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": { "id": 1, "username": "zhangsan", "role": "admin", "has_cookie": true }
  }
}
```

**Errors:** 401 (wrong credentials)

---

### GET /api/auth/me

Get current user info. 🔒 Requires auth.

**Response 200:**
```json
{
  "success": true,
  "data": { "id": 1, "username": "zhangsan", "role": "admin", "has_cookie": true, "created_at": "2026-04-02T10:00:00" }
}
```

---

### GET /api/auth/cookie

Get cookie status (configured or not). 🔒 Requires auth.

**Response 200:**
```json
{ "success": true, "data": { "has_cookie": true } }
```

---

### PUT /api/auth/cookie

Save XHS cookie (encrypted). 🔒 Requires auth.

**Request:**
```json
{ "cookies": "a1=xxx; webId=xxx; web_session=xxx; ..." }
```

**Response 200:**
```json
{ "success": true, "message": "Cookie 保存成功" }
```

---

### POST /api/auth/cookie/check

Check if saved cookie is valid. 🔒 Requires auth.

**Response 200:**
```json
{ "success": true, "data": { "valid": true, "message": "Cookie 有效" } }
```

---

## Content Endpoints

### GET /api/fetch?url={url}

Fetch a Xiaohongshu note by URL. 🔒 Requires auth. 🔒 Requires cookie.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "note_id": "xxx", "title": "...", "description": "...",
    "tags": ["tag1", "tag2"], "images": ["/api/proxy-image?url=..."],
    "author_name": "...", "like_count": 100, "note_type": "normal"
  }
}
```

---

### GET /api/proxy-image?url={url}

Proxy image request to bypass hotlink protection.

---

### GET /api/image-styles

Get available image styles.

**Response 200:**
```json
{
  "styles": [
    { "id": "notebook", "name": "学霸笔记风", "description": "手绘涂鸦 + 莫兰迪色系" },
    { "id": "whiteboard", "name": "白板纪实风", "description": "真实白板过程记录" }
  ]
}
```

---

## Task Endpoints

### POST /api/task

Create a new recreation task. 🔒 Requires auth. 🔒 Requires cookie.

**Request:**
```json
{
  "note_url": "https://www.xiaohongshu.com/explore/xxx",
  "original_title": "...",
  "original_text": "...",
  "tags": ["tag1"],
  "original_images": ["https://..."],
  "image_style_id": "notebook",
  "image_ratio": "3:4",
  "model": "nano-banana-fast"
}
```

**Response 200:**
```json
{ "success": true, "task_id": 123 }
```

---

### GET /api/task/{task_id}

Get task status. 🔒 Requires auth (own tasks only).

---

### GET /api/history?page=1&page_size=20

Get user's task history. 🔒 Requires auth.

---

### DELETE /api/task/{task_id}

Delete a task. 🔒 Requires auth (own tasks only).

---

## WebSocket

### WS /ws/{task_id}

Real-time task progress updates.

---

## Error Format (Unified)

```json
{ "detail": "Human-readable error message" }
```

| Status | Meaning |
|--------|---------|
| 400 | Business error (bad input, no cookie, etc.) |
| 401 | Not authenticated (no/invalid/expired token) |
| 404 | Not found or not your resource |
| 422 | Validation error (Pydantic) |
| 500 | Server error |

---

## Status: Implementation

- ✅ Content endpoints (fetch, proxy, image-styles, task CRUD) — **implemented**
- 🚧 Auth endpoints (register, login, me, cookie) — **in progress** (Login MVP)
- ⚠️ All existing endpoints will require JWT after Login MVP is complete
