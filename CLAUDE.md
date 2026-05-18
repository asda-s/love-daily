# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"心动日常" (Love Daily) — a couples-only private interaction system with two independent sub-projects: `love-backend/` (FastAPI) and `love-frontend/` (UniApp Vue3). Not a monorepo; each has its own dependencies and build system.

## Development Commands

### Backend (love-backend/)

```bash
# Activate venv (located at project root)
source .venv/Scripts/activate   # Windows Git Bash
# or: .venv\Scripts\activate    # Windows CMD

# Install dependencies
pip install -r love-backend/requirements.txt

# Run dev server (from love-backend/)
uvicorn app.main:app --reload

# Production via Docker
cd love-backend && docker-compose up -d
```

### Frontend (love-frontend/)

```bash
cd love-frontend
npm install

# H5 (browser) dev server — proxies API to localhost:8000
npm run dev:h5

# WeChat Mini Program dev
npm run dev:mp-weixin

# Production builds
npm run build:h5
npm run build:mp-weixin
```

No test runner, linter, or formatter is configured.

## Architecture

### Backend Structure (`love-backend/app/`)

Single FastAPI app with 5 routers mounted by domain:

| Router | Prefix | Domain |
|---|---|---|
| `routers/user.py` | `/user` | Auth, registration, profile, lover binding, notifications |
| `routers/memory.py` | `/memory` | Timeline CRUD, anniversary, wish, whisper |
| `routers/life.py` | `/life` | Period tracking, diet, todo, item collection |
| `routers/interact.py` | `/interact` | Checkin, benefits/exchange, emotion, couple ledger |
| `routers/love.py` | `/love` | Love level, achievements, points, level benefits |

Core modules:
- `models.py` — all 17 SQLAlchemy ORM models in one file
- `schemas.py` — all Pydantic request/response models in one file
- `security.py` — JWT auth (HS256, 30-day expiry), bcrypt hashing, `get_current_user` dependency
- `response.py` — unified `success_response()`/`error_response()` returning `{"code": N, "message": "...", "data": ...}`
- `database.py` — engine/session setup; switches between SQLite and MySQL via `DB_TYPE` env var
- `tasks.py` — APScheduler background jobs (anniversary/period/todo reminders at 8:00 AM CST, whisper delivery every minute)

All protected endpoints use `Depends(get_current_user)`. Couple data access uses `or_()` filters to include both partners' data.

### Frontend Structure (`love-frontend/src/`)

UniApp (Vue 3 + Vite) targeting H5 and WeChat Mini Program. 32 pages across 5 tab sections.

Key layers:
- `pages/` — Vue 3 `<script setup>` pages, organized by module (index, user, memory, life, interact, love)
- `store/user.js` — Pinia store for auth state (token, userInfo, loverInfo)
- `store/global.js` — Pinia store for loading/network/system info
- `utils/request.js` — `uni.request` wrapper; auto-attaches Bearer token, shows loading overlay, redirects to login on 401
- `utils/auth.js` — token/userInfo persistence via `uni.setStorageSync`
- `utils/common.js` — date formatting, level info helpers
- `components/custom-tabbar.vue` — custom bottom tab bar (5 tabs: Home, Time, Life, Checkin, Love)

### API Communication

Frontend dev server (port 8080) proxies `/user`, `/memory`, `/life`, `/interact`, `/love`, `/health` to `http://localhost:8000` (configured in `vite.config.js`). JWT token sent as `Authorization: Bearer <token>` header.

### Design System

Primary color: `#FF6B9D` (pink). Light background: `#FFE8F0`. Units in `rpx`. Card border-radius: `16rpx`/`24rpx`. Global SCSS variables in `uni.scss`.

## Known Issues

- **Level thresholds mismatch**: backend `love.py` uses `{1:0, 2:200, 3:500, 4:1000, 5:2000}` but spec and frontend expect `{0-100, 101-300, 301-600, 601-1000, 1001+}`.
- **Duplicated response helpers**: `routers/interact.py` and `routers/love.py` define local `success_response`/`error_response` instead of importing from `app.response`.
- **Image upload stubbed**: `POST /memory/upload` returns a placeholder URL.
- **No git repo initialized** in this project.
