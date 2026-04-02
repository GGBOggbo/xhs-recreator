# 红薯创作坊 — 登录系统 MVP 开发执行计划（ExecPlan）

> 本文档是开发执行的唯一依据。新开一个会话的人只靠此文件即可继续推进。

---

## 1. 产品目标与本期范围总结

**目标**：加一道门，各用各的。

| 维度 | 内容 |
|------|------|
| 访问拦截 | 未登录不能访问任何功能页面，自动跳转登录页 |
| 数据隔离 | 每个用户只能看到自己的任务历史 |
| Cookie 隔离 | 每个用户配置自己的小红书 Cookie，加密存储 |

**本期不做**：管理后台、修改密码、注册开关、邮箱验证、第三方登录、Token 黑名单。

**参考文档**：
- SPEC：`docs/login-system-mvp.md`
- 数据契约：`docs/data-contract.md`

---

## 2. 最小可行技术方案

```
┌─────────────────────────────────────────────────┐
│  浏览器 (Vue 3 SPA)                              │
│                                                   │
│  LoginPage ──→ LandingPage ──→ LinkInput          │
│       │           │               │               │
│  SettingsPage     │          PreviewConfig        │
│                   │               │               │
│               HistoryList    ProgressPanel        │
│                                   │               │
│                              ResultDisplay        │
│                                                   │
│  localStorage: token                              │
│  axios 拦截器: 自动带 Token / 401 跳登录           │
└──────────────────────┬──────────────────────────┘
                       │ Authorization: Bearer <jwt>
                       ▼
┌─────────────────────────────────────────────────┐
│  FastAPI 后端                                     │
│                                                   │
│  /api/auth/*  ─→  不鉴权                          │
│  /api/*       ─→  JWT 中间件 → user_id 注入        │
│                                                   │
│  JWT 中间件                                       │
│    ├─ 解析 Token → user_id                        │
│    ├─ 无 Token → 401                              │
│    └─ 注入 request.state.user_id                  │
│                                                   │
│  Cookie 读取链路：                                 │
│    创建任务时 → 读当前用户 xhs_cookies_encrypted   │
│              → Fernet 解密 → 传给 spider          │
│              → 未配置 → 返回 400                   │
│                                                   │
│  SQLite: users 表 + tasks 表 (加 user_id)         │
└─────────────────────────────────────────────────┘
```

**新增依赖**：`PyJWT`、`bcrypt`、`cryptography`

---

## 3. 推荐的项目结构（新增/改动部分）

```
backend/
├── app/
│   ├── api/
│   │   ├── routes.py          # [改动] 现有接口加鉴权
│   │   └── auth.py            # [新增] 认证相关接口
│   ├── models/
│   │   ├── task.py            # [改动] 加 user_id 字段
│   │   └── user.py            # [新增] User 模型
│   ├── services/
│   │   ├── spider.py          # [改动] 读用户 Cookie
│   │   └── task_runner.py     # [改动] 传 user_id
│   ├── middleware/
│   │   └── auth.py            # [新增] JWT 鉴权中间件
│   ├── utils/
│   │   ├── crypto.py          # [新增] Cookie 加解密
│   │   └── auth.py            # [新增] JWT 生成/验证、密码哈希
│   └── config.py              # [改动] 加 JWT_SECRET_KEY、COOKIE_ENCRYPTION_KEY
├── requirements.txt           # [改动] 加 PyJWT、bcrypt、cryptography
└── .env                       # [改动] 加两个密钥

frontend/
├── src/
│   ├── App.vue                # [改动] 加 login 状态、设置入口、注销按钮
│   ├── utils/
│   │   └── auth.ts            # [新增] Token 管理、axios 拦截器、API 封装
│   └── components/
│       ├── LoginPage.vue      # [新增] 登录/注册页
│       └── SettingsPage.vue   # [新增] Cookie 配置页
```

---

## 4. 需要准备的文档清单

| 文档 | 状态 | 位置 |
|------|------|------|
| MVP SPEC | ✅ 已完成 | `docs/login-system-mvp.md` |
| Data Contract | ✅ 已完成 | `docs/data-contract.md` |
| ExecPlan（本文件） | ✅ 已完成 | `docs/exec-plan.md` |

无需额外文档，以上三份足够。

---

## 5. 开发顺序

**原则**：先后端再前端，先基础设施再业务功能，每个模块可独立验证。

```
Phase 1: 后端基础设施
  M1 → M2 → M3

Phase 2: 后端业务接口
  M4 → M5

Phase 3: 前端基础设施
  M6

Phase 4: 前端业务页面
  M7 → M8

Phase 5: 集成验收
  M9
```

---

## 6. 模块拆分

### M1 — 数据模型 + 数据库迁移

- **目标**：创建 users 表，tasks 表加 user_id
- **输入**：data-contract.md 中的表结构定义
- **输出**：
  - `backend/app/models/user.py`（User 模型）
  - `backend/app/models/task.py` 改动（加 user_id 字段）
  - 数据库迁移执行完成
- **技术约束**：
  - SQLAlchemy ORM，SQLite
  - 密码字段存 bcrypt hash，不存明文
  - 已有 tasks 数据的 user_id 设为 NULL（不破坏）
- **验收标准**：
  - [ ] `users` 表创建成功，字段、类型、约束符合 data-contract
  - [ ] `tasks` 表新增 `user_id` 列，已有数据不受影响
  - [ ] `docker compose restart hongxin-api` 后服务正常启动，无报错

---

### M2 — 工具层（JWT + 密码 + 加密）

- **目标**：提供认证基础设施，被其他模块调用
- **输入**：data-contract.md 中的冻结约定
- **输出**：
  - `backend/app/utils/auth.py`（JWT 生成/验证、bcrypt 哈希/校验）
  - `backend/app/utils/crypto.py`（Fernet 加密/解密）
  - `backend/.env` 新增 `JWT_SECRET_KEY`、`COOKIE_ENCRYPTION_KEY`
  - `backend/requirements.txt` 新增 `PyJWT`、`bcrypt`、`cryptography`
- **技术约束**：
  - JWT 算法 HS256
  - JWT Payload：`{"user_id": int, "username": str, "exp": int}`
  - JWT 有效期 7 天
  - Cookie 加密用 Fernet 对称加密
  - 密钥配在 `.env`，不硬编码
- **验收标准**：
  - [ ] 能生成 JWT 并成功验证
  - [ ] 过期 Token 验证失败
  - [ ] bcrypt 哈希 + 校验通过
  - [ ] Fernet 加密 + 解密还原一致
  - [ ] `docker compose build hongxin-api && docker compose up -d hongxin-api` 后服务正常

---

### M3 — JWT 鉴权中间件

- **目标**：所有 `/api/*` 接口（除注册/登录外）需要 JWT 校验
- **输入**：M2 的 JWT 验证函数
- **输出**：
  - `backend/app/middleware/auth.py`（JWT 校验依赖项）
  - `backend/app/api/routes.py` 改动（所有路由加依赖注入）
- **技术约束**：
  - 使用 FastAPI 的 `Depends()` 机制
  - 白名单路径：`/api/auth/register`、`/api/auth/login`
  - 校验通过后将 `user_id` 注入 `request.state`
  - 无 Token 或无效 → 返回 401 `{"detail": "未登录或登录已过期"}`
- **验收标准**：
  - [ ] 无 Token 访问 `/api/fetch` → 返回 401
  - [ ] 有效 Token 访问 `/api/fetch` → 正常通过
  - [ ] 过期 Token → 返回 401
  - [ ] `/api/auth/register` 和 `/api/auth/login` 不需要 Token

---

### M4 — 认证接口（注册/登录/me）

- **目标**：用户注册、登录、获取信息三个接口
- **输入**：data-contract.md 中 4.1 ~ 4.3 的 API 定义
- **输出**：
  - `backend/app/api/auth.py`（三个接口）
  - `backend/app/main.py` 注册新路由（如需要）
- **技术约束**：
  - username: 3-20 字符，Pydantic 校验
  - password: 最少 6 位，Pydantic 校验
  - 第一个注册用户 role = 'admin'
  - 登录返回 Token + `has_cookie` 布尔值
  - `/api/auth/me` 从 Token 取 user_id 查库
- **验收标准**：
  - [ ] `POST /api/auth/register` 注册成功返回 200
  - [ ] 重复用户名注册返回 400
  - [ ] 第一个注册用户 role 为 admin
  - [ ] `POST /api/auth/login` 登录成功返回 Token + 用户信息
  - [ ] 密码错误返回 401
  - [ ] `GET /api/auth/me` 返回当前用户信息（需 Token）

---

### M5 — Cookie 管理 + 任务用户绑定

- **目标**：Cookie 存取接口 + 现有任务接口按用户隔离
- **输入**：data-contract.md 中 4.4 ~ 4.6 的定义
- **输出**：
  - `backend/app/api/auth.py` 新增 Cookie 相关接口
  - `backend/app/api/routes.py` 改造（任务创建绑 user_id，查询按用户过滤）
  - `backend/app/services/spider.py` 改造（读用户 Cookie）
  - `backend/app/services/task_runner.py` 改造（传入用户 Cookie）
- **技术约束**：
  - PUT Cookie 时用 Fernet 加密后存库
  - Cookie 检测：实际调用一次 `get_note_info` 验证
  - 任务创建时从 `request.state.user_id` 取用户 ID
  - 查询历史/任务详情时 WHERE user_id = current_user_id
  - 用户未配置 Cookie → 返回 400 提示
- **验收标准**：
  - [ ] PUT Cookie 保存成功，数据库中为加密密文
  - [ ] Cookie 检测有效返回 `valid: true`
  - [ ] Cookie 检测无效返回 `valid: false`
  - [ ] 未配置 Cookie 时创建任务返回 400
  - [ ] 用户 A 创建的任务，用户 B 的历史查不到
  - [ ] `/api/fetch` 使用当前用户的 Cookie 爬取

---

### M6 — 前端基础设施（Token 管理 + axios 拦截）

- **目标**：全局 auth 状态管理，所有请求自动带 Token，401 自动跳登录
- **输入**：data-contract.md 中的 Token 约定
- **输出**：
  - `frontend/src/utils/auth.ts`（Token 存取、axios 拦截器、API 封装）
- **技术约束**：
  - Token 存 `localStorage`，key 为 `xhs_token`
  - axios 请求拦截器自动加 `Authorization: Bearer <token>`
  - axios 响应拦截器：401 → 清 Token → 跳登录页
  - 所有后端 API 调用统一走这个 axios 实例
- **验收标准**：
  - [ ] 登录后 Token 存入 localStorage
  - [ ] 后续请求自动带 Authorization header
  - [ ] Token 过期后自动跳转登录页
  - [ ] 注销后 Token 被清除

---

### M7 — 登录/注册页

- **目标**：登录和注册的完整 UI 和交互
- **输入**：M4 的注册/登录接口
- **输出**：
  - `frontend/src/components/LoginPage.vue`
  - `frontend/src/App.vue` 改动（新增 login 状态、登录态判断）
- **技术约束**：
  - 登录/注册在同一个组件内切换（Tab 或链接切换）
  - 登录成功后跳转到首页（landing）或上一次页面
  - 已登录状态下直接访问 `/login` → 跳首页
  - 页面风格与现有项目一致
- **验收标准**：
  - [ ] 输入用户名密码 → 注册成功 → 提示 → 切换到登录表单
  - [ ] 输入用户名密码 → 登录成功 → 跳转首页
  - [ ] 用户名/密码格式错误 → 前端提示
  - [ ] 服务端错误 → 显示错误信息
  - [ ] 已登录状态刷新页面不跳登录页

---

### M8 — 设置页 + 导航栏改造

- **目标**：Cookie 配置页面 + 导航栏显示用户名/设置入口/注销
- **输入**：M5 的 Cookie 管理接口
- **输出**：
  - `frontend/src/components/SettingsPage.vue`
  - `frontend/src/App.vue` 改动（导航栏用户名 + 设置 + 注销）
- **技术约束**：
  - Cookie 输入框用 textarea，多行粘贴
  - 「检测有效性」按钮 → 调用 check 接口 → 显示结果
  - 「保存」按钮 → 调用 PUT 接口
  - 未配置 Cookie 时，设置页有引导文案
  - 导航栏右侧：用户名 | 设置图标 | 注销按钮
- **验收标准**：
  - [ ] 粘贴 Cookie → 点保存 → 成功提示
  - [ ] 点「检测有效性」→ 显示有效/无效
  - [ ] 导航栏显示当前用户名
  - [ ] 点注销 → 清 Token → 跳登录页
  - [ ] 点设置 → 进入设置页

---

### M9 — 集成验收

- **目标**：完整二创流程端到端跑通
- **输入**：所有模块完成
- **输出**：MVP 验收通过
- **验收标准**（逐条检查）：
  - [ ] 未登录访问任何页面 → 自动跳转登录页
  - [ ] 注册 → 登录 → 进入首页，流程无断点
  - [ ] 用户 A 创建的任务，用户 B 的历史记录里看不到
  - [ ] 第一个注册的用户，数据库 role 字段为 admin
  - [ ] 用户可以在设置页填写 Cookie，检测通过后保存
  - [ ] **完整二创流程**：输入链接 → 预览 → 选风格 → 生成 → 结果 → 历史记录，登录前后均无异常
  - [ ] Docker Compose 构建部署无报错

---

## 7. 风险点与待确认问题

| # | 问题 | 影响 | 建议 |
|---|------|------|------|
| R1 | 开放注册，任何人可注册 | 与内部使用矛盾 | MVP 接受，后续加注册开关 |
| R2 | JWT 注销后仍在有效期内可用 | 安全风险 | MVP 接受，后续加黑名单 |
| R3 | 已有 tasks 数据 user_id 为 NULL | 首个用户登录后历史为空 | 可接受，旧数据可手动关联 |
| R4 | Fernet 密钥更换 → 已有 Cookie 全失效 | 用户需重配 | `.env` 注释说明，密钥生成后不动 |
| R5 | Dockerfile.backend 需新增依赖 | 需重新 build 镜像 | M2 阶段更新 requirements.txt 并 rebuild |

---

## 8. 适合 AI 直接完成的模块

| 模块 | 理由 |
|------|------|
| M1 数据模型 | 结构明确，data-contract 已定义 |
| M2 工具层 | 纯函数，输入输出清晰，无 UI |
| M3 JWT 中间件 | FastAPI 标准模式，文档充分 |
| M4 认证接口 | API Contract 已定义，CRUD 标准 |
| M6 前端基础设施 | Token 管理 + axios 拦截，模式固定 |

**共 5/9 个模块可由 AI 独立完成。**

---

## 9. 需要人工拍板的部分

| 模块 | 需要拍板的内容 | 理由 |
|------|---------------|------|
| M7 登录页 | UI 样式、布局、交互细节 | 视觉偏好因人而异 |
| M8 设置页 | Cookie 输入框交互、引导文案 | 用户体验相关 |
| M8 导航栏 | 注销按钮位置、用户名显示方式 | 影响全局布局 |
| M9 集成验收 | 最终验收测试 | 需要人工操作确认 |

---

## 10. Progress

> 每个 checkbox 记录完成时间。格式：`- [ ] YYYY-MM-DD HH:MM — 描述`

### Phase 1: 后端基础设施

- [ ] M1 数据模型 + 数据库迁移
  - [ ] 创建 `backend/app/models/user.py`
  - [ ] 改造 `backend/app/models/task.py`（加 user_id）
  - [ ] 执行数据库迁移（ALTER TABLE）
  - [ ] 重启服务验证无报错

- [ ] M2 工具层（JWT + 密码 + 加密）
  - [ ] 创建 `backend/app/utils/auth.py`
  - [ ] 创建 `backend/app/utils/crypto.py`
  - [ ] 更新 `.env` 新增密钥
  - [ ] 更新 `requirements.txt`
  - [ ] 重建 Docker 镜像验证依赖安装

- [ ] M3 JWT 鉴权中间件
  - [ ] 创建 `backend/app/middleware/auth.py`
  - [ ] 改造 `backend/app/api/routes.py`（加依赖注入）
  - [ ] curl 测试：无 Token → 401，有 Token → 通过

### Phase 2: 后端业务接口

- [ ] M4 认证接口（注册/登录/me）
  - [ ] 创建 `backend/app/api/auth.py`
  - [ ] 注册接口测试
  - [ ] 登录接口测试
  - [ ] me 接口测试

- [ ] M5 Cookie 管理 + 任务用户绑定
  - [ ] Cookie 管理接口（PUT / check）
  - [ ] spider.py 改造（读用户 Cookie）
  - [ ] 任务创建绑定 user_id
  - [ ] 历史查询按用户过滤
  - [ ] 多用户隔离测试

### Phase 3: 前端基础设施

- [ ] M6 前端 Token 管理 + axios 拦截
  - [ ] 创建 `frontend/src/utils/auth.ts`
  - [ ] axios 拦截器测试
  - [ ] 401 自动跳转测试

### Phase 4: 前端业务页面

- [ ] M7 登录/注册页
  - [ ] 创建 `LoginPage.vue`
  - [ ] 改造 `App.vue`（login 状态）
  - [ ] 注册 → 登录 → 首页 流程测试

- [ ] M8 设置页 + 导航栏改造
  - [ ] 创建 `SettingsPage.vue`
  - [ ] 导航栏用户名 + 设置 + 注销
  - [ ] Cookie 配置 → 检测 → 保存 测试

### Phase 5: 集成验收

- [ ] M9 集成验收
  - [ ] 验收标准 1：未登录拦截
  - [ ] 验收标准 2：注册登录流程
  - [ ] 验收标准 3：任务隔离
  - [ ] 验收标准 4：首任管理员
  - [ ] 验收标准 5：Cookie 配置
  - [ ] 验收标准 6：完整二创流程
  - [ ] 验收标准 7：Docker 部署
  - [ ] Git commit 全部改动

---

## 11. Surprises & Discoveries

> 开发过程中记录意料之外的问题。

*（开发开始后填写）*

---

## 12. Decision Log

> 记录开发过程中做出的关键决策及理由。

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| D1 | Cookie 隔离放入 MVP | 没有它登录意义打折 | 2026-04-02 |
| D2 | 管理员 MVP 无额外权限 | 留标记够用，不提前开发空功能 | 2026-04-02 |
| D3 | 用户未配 Cookie 不降级到全局 | 强制隔离，避免混淆 | 2026-04-02 |
| D4 | Cookie 检测用 get_note_info | 最直接的验证方式 | 2026-04-02 |
| D5 | 路由白名单方式做鉴权 | 比 exclude_path 更直观可控 | 待开发时确认 |

---

## 13. Outcomes & Retrospective

> MVP 完成后回顾。

*（MVP 验收通过后填写）*

**回顾问题：**
- 实际开发耗时 vs 预期？
- 哪些模块比预期复杂？
- 哪些决策后来被证明是对的/错的？
- MVP 验收中有哪些意外发现？
- 下一个迭代应该优先做什么？
