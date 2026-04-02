# 红薯创作坊 — 用户登录系统 MVP SPEC（v2）

## 问题陈述

项目目前无访问控制，所有访问者共享同一份 XHS Cookie，任务历史无归属。需要一套基础的用户系统，实现访问拦截、数据隔离、Cookie 隔离。

## 目标用户

自己 / 小团队内部使用，私有部署。

## 核心场景

| # | 场景 | 角色 |
|---|------|------|
| S1 | 未登录用户访问任何页面 → 被重定向到登录页 | 游客 |
| S2 | 游客注册账号 → 跳转登录页 | 游客 |
| S3 | 用户登录 → 进入首页，开始使用 | 注册用户 |
| S4 | 用户注销 → 回到登录页 | 注册用户 |
| S5 | 用户创建二创任务 → 任务自动绑定当前用户 | 注册用户 |
| S6 | 用户查看历史记录 → 只看到自己的任务 | 注册用户 |
| S7 | 用户首次登录 / 未配置 Cookie → 页面提示引导前往设置页 | 注册用户 |
| S8 | 用户在设置页填写/更新 XHS Cookie → 点击「检测有效性」→ 保存成功 | 注册用户 |
| S9 | 用户未配置 Cookie 时创建任务 → 提示「请先配置小红书 Cookie」 | 注册用户 |

## 方案描述

- 后端（FastAPI）新增 `users` 表，接口增加 JWT 鉴权中间件
- 前端（Vue 3）新增登录/注册页面 + 设置页面，未登录状态拦截跳转
- 现有 `tasks` 表增加 `user_id` 外键，查询时按用户过滤
- 每个用户独立存储自己的 XHS Cookie（加密），任务执行时读取当前用户的 Cookie
- Token 存储在 `localStorage`，请求时通过 `Authorization: Bearer <token>` 携带

## 核心功能

### F1 — 用户注册
- POST `/api/auth/register`
- 参数：`username`（3-20字符）、`password`（6位以上）
- 第一个注册的用户自动标记为 `admin` 角色
- 注册成功返回提示，需登录

### F2 — 用户登录
- POST `/api/auth/login`
- 参数：`username`、`password`
- 返回 JWT Token + 用户信息（含角色、是否已配置 Cookie）
- Token 有效期 7 天

### F3 — 获取当前用户信息
- GET `/api/auth/me`
- 根据 Token 返回当前用户信息（含是否已配置 Cookie）

### F4 — 注销
- 前端清除 localStorage 中的 Token，跳转到登录页
- 无需后端接口（JWT 无状态）

### F5 — 任务绑定用户
- 创建任务时自动写入当前 `user_id`
- 查询历史/任务详情时只能查到自己的

### F6 — 现有接口鉴权
- 所有 `/api/*` 接口（除注册/登录外）增加 JWT 校验
- 无 Token 或 Token 过期返回 401

### F7 — Cookie 管理
- GET `/api/auth/cookie` — 获取当前用户的 Cookie 状态（已配置/未配置，不返回明文）
- PUT `/api/auth/cookie` — 保存/更新用户 Cookie（加密存储）
- POST `/api/auth/cookie/check` — 检测当前 Cookie 有效性（实际调用一次小红书 API 验证）

### F8 — Cookie 读取
- 创建任务时，从当前用户的加密 Cookie 读取
- 用户未配置 Cookie 时，返回提示信息，不降级使用服务端全局 Cookie

## 技术约束

| 项 | 选型 |
|----|------|
| 后端框架 | FastAPI（现有） |
| 前端框架 | Vue 3 + TypeScript（现有） |
| 数据库 | SQLite + SQLAlchemy（现有） |
| 认证方案 | JWT（`PyJWT` 库） |
| 密码存储 | `bcrypt` 哈希，不明文 |
| Cookie 加密 | 对称加密（`cryptography` 库 Fernet），密钥配在 `.env` 的 `COOKIE_ENCRYPTION_KEY` |
| Token 存储 | 前端 `localStorage` |
| 数据库迁移 | 手动 ALTER TABLE（现有模式） |

## 明确不做的事（MVP 之后）

- ❌ 用户管理后台（管理员 CRUD 用户）
- ❌ 修改密码 / 忘记密码
- ❌ 注册开关 / 邀请码
- ❌ 邮箱验证
- ❌ 第三方登录（微信/GitHub）
- ❌ 管理员额外权限（MVP 里 admin 和普通用户完全一样，只是数据库标记）

## 成功标准

1. 未登录访问任何页面 → 自动跳转登录页
2. 注册 → 登录 → 正常使用二创功能，流程无断点
3. 用户 A 的历史记录，用户 B 看不到
4. 第一个注册用户自动为管理员
5. 用户可以在设置页配置自己的 Cookie，检测有效性通过后保存
6. 未配置 Cookie 时创建任务 → 收到明确提示
7. **登录前后，完整二创流程跑通**：输入链接 → 预览 → 选风格 → 生成 → 结果 → 历史记录，所有环节无异常

## 风险与待确认问题

| # | 风险/待确认 | 影响 | 处理方式 |
|---|------------|------|---------|
| R1 | 开放注册 + 内部部署 = 任何人可注册 | 后续需加注册开关 | 标记为已知，不阻塞 MVP |
| R2 | JWT 无状态 → 注销后 Token 在有效期内仍可用 | 安全风险 | MVP 可接受，后续加黑名单 |
| R3 | SQLite 并发写入限制 | 小团队无影响 | 不处理 |
| R4 | 加密密钥更换后已存储 Cookie 全部失效 | 用户需重新配置 | SPEC 标注，密钥生成后不变 |
| R5 | 用户 Cookie 过期后需手动更新 | 体验中断 | 设置页提供检测按钮，任务失败时提示 |

## MVP 范围

### 后端改动

1. **新增 `User` 模型**（users 表）
   - `id`, `username`, `password_hash`, `role`（admin/user）, `xhs_cookies_encrypted`, `created_at`
2. **新增认证接口**
   - `/api/auth/register` — 注册
   - `/api/auth/login` — 登录，返回 JWT
   - `/api/auth/me` — 获取当前用户信息
3. **新增 Cookie 管理接口**
   - `/api/auth/cookie` GET — Cookie 状态
   - `/api/auth/cookie` PUT — 保存 Cookie（加密）
   - `/api/auth/cookie/check` POST — 检测有效性
4. **新增 JWT 中间件**
   - 保护现有 `/api/*` 接口（除注册/登录外）
   - 从 Token 解析 `user_id`，注入请求上下文
5. **改造现有接口**
   - `tasks` 表增加 `user_id` 列
   - 创建任务时自动写入当前 `user_id`
   - 查询历史/任务详情时按 `user_id` 过滤
   - `spider.py` 的 `fetch_note` 优先读用户 Cookie，未配置则返回提示
6. **新增依赖**
   - `PyJWT` — JWT 生成/验证
   - `bcrypt` — 密码哈希
   - `cryptography` — Cookie 加密

### 前端改动

1. **新增 `LoginPage.vue`**（登录/注册二合一页面）
2. **新增 `SettingsPage.vue`**（Cookie 配置 + 检测有效性）
3. **新增 auth 状态管理**（localStorage + axios 拦截器）
   - 登录状态判断
   - Token 自动携带
   - 401 自动跳转登录页
4. **修改 `App.vue`**
   - 新增 `currentStep = 'login'` 状态
   - 导航栏增加「设置」入口
   - 导航栏显示用户名 + 注销按钮
5. **修改所有 API 请求**
   - 携带 Authorization header
   - 处理 401 响应

### 数据库变更

```sql
-- 新增 users 表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(10) DEFAULT 'user',
    xhs_cookies_encrypted TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- tasks 表新增 user_id 列
ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id);
```
