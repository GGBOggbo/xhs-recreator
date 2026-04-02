# AGENTS.md — XHS ReCreator Project Context

> This file is the single entry point for any AI agent working on this project.
> Read this first, then follow links to specifics.

## What Is This Project

**红薯创作坊 (XHS ReCreator)** — AI-powered Xiaohongshu (Little Red Book) content recreation tool.

Users paste a Xiaohongshu note URL, the system fetches the original content (text + images), then uses multi-modal AI to rewrite the text and generate new images in a chosen style.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.x, FastAPI, SQLAlchemy, SQLite |
| Frontend | Vue 3, TypeScript, Vite, Tailwind CSS v4 |
| AI | ZhipuAI (GLM-4V vision, GLM-4 text), NanoBanana (image gen) |
| Crawling | Spider_XHS (custom, uses JS signature generation) |
| Deployment | Docker Compose (nginx frontend + FastAPI backend) |

## Project Structure

```
/data/project/xhs_recreator/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # REST API endpoints
│   │   ├── api/websocket.py       # WebSocket progress updates
│   │   ├── application/steps.py   # Pure business functions (no DB/IO)
│   │   ├── config.py              # Settings + prompt config
│   │   ├── domain/interfaces.py   # CrawlerProvider protocol
│   │   ├── models/task.py         # Task ORM model
│   │   ├── services/
│   │   │   ├── spider.py          # SpiderXHSAdapter (implements CrawlerProvider)
│   │   │   ├── task_runner.py     # Orchestrates the 5-step recreation pipeline
│   │   │   ├── llm.py             # ZhipuAI text generation
│   │   │   ├── vision.py          # ZhipuAI image analysis
│   │   │   └── image_gen.py       # NanoBanana image generation
│   │   └── utils/helpers.py       # Utility functions
│   ├── prompts.yaml               # All AI prompts (system, vision, image styles)
│   ├── .env                       # Secrets (NEVER commit)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue                # Root SPA (currentStep state machine)
│   │   ├── main.ts
│   │   ├── tailwind.css
│   │   └── components/
│   │       ├── LandingPage.vue    # Product landing page
│   │       ├── LinkInput.vue      # Step 1: URL input
│   │       ├── PreviewConfig.vue  # Step 2: Preview + configure
│   │       ├── ProgressPanel.vue  # Step 3: Progress tracking
│   │       ├── ResultDisplay.vue  # Step 4: Show results
│   │       └── HistoryList.vue    # Past tasks
│   └── vite.config.ts
├── spider_xhs/                    # Third-party XHS crawler (mounted read-only)
├── docs/                          # Product & development docs
├── data/                          # SQLite DB + runtime data
├── output/                        # Generated images + texts
├── docker-compose.yml
├── Dockerfile.backend
└── Dockerfile.frontend
└── nginx.conf
```

## Key Architecture Decisions

1. **SPA without vue-router** — Navigation via `currentStep` ref in App.vue
2. **Protocol pattern for crawlers** — `CrawlerProvider` interface in `domain/interfaces.py`, `SpiderXHSAdapter` implements it
3. **Steps pattern** — Pure functions in `application/steps.py` (no DB/WebSocket), orchestrated by `task_runner.py`
4. **Constructor injection** — `TaskRunner(crawler: CrawlerProvider = spider_service)`
5. **No vue-router** — All page switching via `currentStep` state variable + `sessionStorage` for persistence
6. **SQLite with manual migration** — No Alembic, use `ALTER TABLE` directly

## Development Rules

### General
- Commit after each meaningful change (`git commit`)
- Never commit `.env` or secrets
- Rebuild Docker images after dependency changes: `docker compose build && docker compose up -d`
- Restart API after `.env` changes requires `docker compose up -d hongxin-api` (NOT just `restart`)

### Backend
- Follow existing code style (loguru logging, pydantic models, FastAPI dependency injection)
- New dependencies go in `requirements.txt` + rebuild Docker image
- Database changes: manual `ALTER TABLE` + update SQLAlchemy model
- Spider_XHS is mounted read-only — do not modify it unless absolutely necessary

### Frontend
- Vue 3 `<script setup lang="ts">` pattern
- Scoped CSS, Tailwind utility classes for new components
- API calls should use the shared axios instance (with interceptors)
- All state in App.vue via `currentStep` — no vue-router

## Current Development Phase

**Login System MVP** — Adding user authentication, task isolation, and per-user Cookie management.

See: [docs/exec-plan.md](docs/exec-plan.md) for full execution plan.

## Documentation Index

| Document | Purpose |
|----------|---------|
| [docs/product-spec.md](docs/product-spec.md) | Product overview and context |
| [docs/mvp.md](docs/mvp.md) | Login system MVP spec |
| [docs/data-contract.md](docs/data-contract.md) | Data models + API contracts |
| [docs/api.md](docs/api.md) | API endpoint reference |
| [docs/exec-plan.md](docs/exec-plan.md) | Development execution plan |
| [docs/tasks/](docs/tasks/) | Individual task files (task-001 ~ task-012) |
| [PROGRESS.md](PROGRESS.md) | Current status and next steps |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture details |

## Pending Confirmations

- [ ] R1: Open registration vs internal use — need registration switch in future
- [ ] R2: JWT logout blacklist — deferred to post-MVP
- [ ] Admin panel features — deferred to post-MVP
