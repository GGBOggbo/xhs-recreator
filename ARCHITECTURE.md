# ARCHITECTURE.md — XHS ReCreator

## System Overview

```
┌──────────────┐       ┌──────────────┐       ┌─────────────────┐
│   Browser    │  HTTP │    Nginx     │  HTTP │   FastAPI API   │
│   (Vue 3)    │◄─────►│  (:80)       │◄─────►│   (:8000)       │
│   SPA        │       │  / → static  │       │   /api/*        │
└──────────────┘       │  /api → api  │       │   /ws/*         │
                       └──────────────┘       └────┬────────────┘
                                                   │
                                    ┌──────────────┼──────────────┐
                                    │              │              │
                               ┌────▼───┐    ┌────▼───┐    ┌────▼───┐
                               │Spider  │    │ZhipuAI │    │Nano    │
                               │XHS     │    │LLM/Vis │    │Banana  │
                               │(crawl) │    │(AI)    │    │(image) │
                               └────────┘    └────────┘    └────────┘
                                                   │
                                              ┌────▼────┐
                                              │ SQLite  │
                                              │ (data/) │
                                              └─────────┘
```

## Backend Architecture

### Layered Design

```
api/              → Routes (HTTP handlers, request/response, validation)
├── routes.py     → Business endpoints (CRUD, fetch, task management)
└── websocket.py  → Real-time progress updates

services/         → Business logic (orchestration)
├── spider.py     → SpiderXHSAdapter (implements CrawlerProvider)
├── task_runner.py→ 5-step recreation pipeline orchestrator
├── llm.py        → ZhipuAI text generation
├── vision.py     → ZhipuAI image analysis
└── image_gen.py  → NanoBanana image generation

application/      → Pure business functions (no side effects)
└── steps.py      → fetch_note_step, analyze_images_step, etc.

domain/           → Interfaces and contracts
└── interfaces.py → CrawlerProvider protocol, NoteData/NoteContent

models/           → ORM models
└── task.py       → Task SQLAlchemy model

config.py         → Settings (pydantic-settings), PromptConfig (YAML)
```

### Dependency Flow

```
routes.py → task_runner.py → steps.py (pure functions)
         → spider.py (implements CrawlerProvider)
         → llm.py / vision.py / image_gen.py
```

### Task Pipeline (5 steps)

1. **fetch_note** — Crawl XHS note via Spider_XHS
2. **analyze_images** — Vision AI analyzes original images
3. **rewrite_content** — LLM rewrites the text
4. **generate_images** — Image AI creates new images
5. **save_result** — Write output to disk + update DB

Each step is a pure function in `steps.py`. `task_runner.py` orchestrates them with DB/WebSocket/logging.

## Frontend Architecture

### State Machine (no vue-router)

```
currentStep: 'login' | 'landing' | 'input' | 'preview' | 'processing' | 'result' | 'history' | 'settings'
```

- Default: `'login'` (after login system is added)
- Persisted to `sessionStorage` for refresh survival
- Token persisted to `localStorage`

### Component Tree

```
App.vue
├── LoginPage.vue        (currentStep === 'login')
├── LandingPage.vue      (currentStep === 'landing')
├── LinkInput.vue        (currentStep === 'input')
├── PreviewConfig.vue    (currentStep === 'preview')
├── ProgressPanel.vue    (currentStep === 'processing')
├── ResultDisplay.vue    (currentStep === 'result')
├── SettingsPage.vue     (currentStep === 'settings')
└── HistoryList.vue      (currentStep === 'history')
```

## Data Model

### Current (pre-login)

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    note_url TEXT,
    title TEXT,
    original_text TEXT,
    rewritten_text TEXT,
    tags TEXT,            -- JSON array
    original_images TEXT, -- JSON array
    generated_images TEXT,-- JSON array
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    image_style_id VARCHAR(30) DEFAULT 'notebook'
);
```

### Post-Login MVP (target)

```sql
-- NEW
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(10) DEFAULT 'user',
    xhs_cookies_encrypted TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MODIFIED
ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id);
```

## Deployment

```yaml
# docker-compose.yml
hongxin-api:  # FastAPI backend
  - Port 8000
  - Mounts: .env, prompts.yaml, output/, data/, spider_xhs/ (read-only)

hongxin-web:  # Nginx serving built Vue SPA + reverse proxy
  - Port 80
  - Builds frontend at image build time (COPY + npm build)
  - nginx.conf: / → static, /api → proxy to hongxin-api:8000
```

### Key deployment note

- **Code changes**: require `docker compose build` + `docker compose up -d`
- **.env changes**: require `docker compose up -d` (recreate container)
- **Volume-mounted files** (prompts.yaml): only need `docker compose restart`
