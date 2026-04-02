# Cursor Rules — XHS ReCreator

## Project Context

Read [AGENTS.md](../../AGENTS.md) for full project context.

## Rules

- Backend: Python (FastAPI + SQLAlchemy), follow existing patterns in `backend/app/`
- Frontend: Vue 3 + TypeScript, `<script setup lang="ts">`, scoped CSS
- No vue-router — all page switching via `currentStep` in App.vue
- Spider_XHS (`spider_xhs/`) is read-only — do not modify unless explicitly asked
- `.env` files contain secrets — never suggest committing them
- After code changes, rebuild Docker: `docker compose build && docker compose up -d`

## Current Task

See [PROGRESS.md](../../PROGRESS.md) for current development status.
