# 红薯创作坊 — 登录系统 MVP（第一版）

---

## 1. MVP 的目标

一句话：**加一道门，各用各的。**

- 未登录不能访问功能（访问拦截）
- 每个人的任务历史只看自己的（数据隔离）
- 每个人填自己的小红书 Cookie（Cookie 隔离）

就这三件事，其他一律不做。

---

## 2. MVP 必须做的功能

### 后端（5 个接口）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 注册，第一个用户自动 admin |
| `/api/auth/login` | POST | 登录，返回 JWT |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/auth/cookie` | PUT | 保存用户 Cookie（加密） |
| `/api/auth/cookie/check` | POST | 检测 Cookie 是否有效 |

### 后端（改造）

- 所有 `/api/*` 接口加 JWT 校验（注册/登录除外）
- `tasks` 表加 `user_id`，创建任务自动写入，查询时按用户过滤
- 爬虫读用户自己的 Cookie，没配则返回提示

### 前端（2 个新页面）

| 页面 | 说明 |
|------|------|
| `LoginPage.vue` | 登录 + 注册，二合一 |
| `SettingsPage.vue` | Cookie 配置 + 检测有效性按钮 |

### 前端（改造）

- `App.vue`：新增 `login` 状态，未登录拦截跳转
- 导航栏：加用户名 + 设置入口 + 注销按钮
- 所有 API 请求携带 Token，401 自动跳登录页

### 数据库

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(10) DEFAULT 'user',
    xhs_cookies_encrypted TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id);
```

---

## 3. 第一版明确不做的功能

- ❌ 用户管理后台（管理员 CRUD）
- ❌ 修改密码 / 忘记密码
- ❌ 注册开关 / 邀请码 / 邮箱验证
- ❌ 第三方登录
- ❌ 管理员额外权限（MVP 里 admin = 普通用户，只是数据库标记）
- ❌ 注销后 Token 黑名单
- ❌ Cookie GET 接口（前端只需知道有没有配，登录返回里带个布尔值就够）

---

## 4. 最小用户闭环

```
注册 → 登录 → 首页 → 进入设置页 → 填写 Cookie → 检测通过 → 保存
  → 回到首页 → 输入链接 → 预览 → 选风格 → 生成 → 查看结果 → 历史记录
  → 注销 → 回到登录页
```

任何一个环节断开，MVP 就没完成。

---

## 5. 为什么这样切分

| 决策 | 理由 |
|------|------|
| Cookie 隔离放进 MVP | 不做的话登录意义打折，所有人还是用同一个 Cookie |
| Cookie 检测放进 MVP | 不做的话用户填了无效 Cookie 也不知道，到创建任务时才报错，体验差 |
| 管理后台不做 | 内部小团队，手动改数据库就行，不值得开发 |
| Token 黑名单不做 | JWT 7 天过期，内部使用可接受，后续再加 |
| 密码修改不做 | 内部用，忘了直接改数据库 |
| admin 权限不做 | 留个标记够用，不提前开发空功能 |

---

## 6. MVP 验收标准

跑通以下 6 条，MVP 即完成：

- [ ] 未登录访问任何页面 → 自动跳转登录页
- [ ] 注册 → 登录 → 进入首页，流程无断点
- [ ] 用户 A 创建的任务，用户 B 的历史记录里看不到
- [ ] 第一个注册的用户，数据库 role 字段为 admin
- [ ] 用户可以在设置页填写 Cookie，点击检测按钮验证通过后保存
- [ ] **完整二创流程跑通**：输入链接 → 预览 → 选风格 → 生成 → 结果 → 历史记录，登录前后均无异常
