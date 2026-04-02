# Task Files 索引

## 总览

| 编号 | 任务名 | 执行者 | 依赖 | Phase |
|------|--------|--------|------|-------|
| [task-001](task-001.md) | 数据模型 + 数据库迁移 | 🤖 AI | 无 | Phase 1 |
| [task-002](task-002.md) | 认证工具层 — JWT + bcrypt | 🤖 AI | 无 | Phase 1 |
| [task-003](task-003.md) | 加密工具层 — Fernet | 🤖 AI | 无 | Phase 1 |
| [task-004](task-004.md) | JWT 鉴权中间件 + 路由保护 | 🤖 AI | task-002 | Phase 1 |
| [task-005](task-005.md) | 认证接口 — 注册/登录/Me | 🤖 AI | task-001, 002 | Phase 2 |
| [task-006](task-006.md) | Cookie 管理接口 | 🤖 AI | task-003, 004, 005 | Phase 2 |
| [task-007](task-007.md) | 任务用户绑定 | 🤖 AI | task-004, 005 | Phase 2 |
| [task-008](task-008.md) | 前端认证基础设施 | 🤖 AI | 无（可与后端并行） | Phase 3 |
| [task-009](task-009.md) | 登录/注册页面 | ⚠️ 需拍板 UI | task-008 | Phase 4 |
| [task-010](task-010.md) | 设置页 — Cookie 配置 | ⚠️ 需拍板交互 | task-006, 008 | Phase 4 |
| [task-011](task-011.md) | 导航栏改造 | ⚠️ 需拍板布局 | task-008 | Phase 4 |
| [task-012](task-012.md) | 集成验收 | ⚠️ 人工操作 | 全部 | Phase 5 |

## 依赖图

```
task-001 (DB模型)  ──┐
                      ├─→ task-005 (认证接口) ──┬→ task-006 (Cookie接口)
task-002 (JWT+bcrypt) ┤                        └→ task-007 (任务绑定)
         │            │
         └─→ task-004 (中间件) ──→ task-005/006/007

task-003 (Fernet) ─────────────→ task-006 (Cookie接口)

task-008 (前端auth) ──→ task-009 (登录页)
                   ──→ task-010 (设置页)
                   ──→ task-011 (导航栏)

全部 ──→ task-012 (集成验收)
```

## 可并行组合

- **Phase 1**：task-001、task-002、task-003 可完全并行（无依赖）
- **Phase 3**：task-008 可与 Phase 2 后端任务并行
- **Phase 4**：task-009、task-010、task-011 有依赖但可由同一人顺序做

## 执行者说明

- 🤖 **AI 直接完成**：task-001 ~ task-008（共 8 个，输入输出清晰，无 UI 判断）
- ⚠️ **需人工拍板**：task-009 ~ task-012（共 4 个，涉及 UI 样式/交互/最终验收）
