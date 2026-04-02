# CLAUDE.md — Claude Code Specific Rules

> This file supplements AGENTS.md with Claude-specific instructions.
> AGENTS.md is the source of truth for project context; this file only adds Claude rules.

## Read First

See [AGENTS.md](AGENTS.md) for full project context, tech stack, and documentation index.

## Claude Code Rules

### Commit Discipline
- Commit after each meaningful change with descriptive messages
- Use Chinese for commit messages when the change is user-facing
- Always include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` in commits

### Docker Operations
- Backend code changes require `docker compose build hongxin-api && docker compose up -d hongxin-api`
- Frontend code changes require `docker compose build hongxin-web && docker compose up -d hongxin-web`
- `.env` changes require `docker compose up -d hongxin-api` (recreate container, NOT just restart)
- Always `cd /data/project/xhs_recreator` before docker compose commands

### File References
- Use markdown link syntax: `[file.py](path/to/file.py)` not backticks or HTML
- Include line numbers for specific code: `[file.py:42](path/to/file.py#L42)`

### Code Style
- Backend: Follow existing patterns in the codebase (loguru, pydantic, FastAPI)
- Frontend: Vue 3 `<script setup lang="ts">`, scoped CSS
- Do not add comments/docstrings to code you didn't change
- Do not add error handling for scenarios that can't happen

### Language
- Respond in Chinese when the user communicates in Chinese
- Keep responses concise — no unnecessary summaries or filler

### Current Focus
- **Login System MVP** is the active development phase
- See [PROGRESS.md](PROGRESS.md) for current task status
- Pick up from the next incomplete task in the task list
