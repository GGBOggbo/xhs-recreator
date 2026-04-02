# Windsurf Rules — XHS ReCreator

Read [AGENTS.md](../../AGENTS.md) for full project context.

## Rules

- Follow patterns in existing code — don't introduce new paradigments
- Backend: FastAPI + SQLAlchemy + SQLite, see `backend/app/`
- Frontend: Vue 3 `<script setup lang="ts">`, no vue-router
- Spider_XHS (`spider_xhs/`) is read-only
- `.env` is secrets — never commit
- Docker rebuild required after code changes

## Current Focus

Login System MVP — see [PROGRESS.md](../../PROGRESS.md)
