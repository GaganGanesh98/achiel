# CampusVoice

A verified-student platform for sharing experiences about **German universities and Hochschulen** — study life, cost of living, culture, and campus topics. Only students with verified email domains at accredited German institutions can post.

## Stack

- **Backend**: FastAPI (Python 3.11), PostgreSQL 16, Redis 7, SQLAlchemy 2.0, Alembic, JWT auth
- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Deployment**: Railway (matches your Axiom setup)

## MVP Scope

1. Email-domain-based student verification (`@*.edu`, `@*.ac.in`, university domains via allowlist)
2. Authenticated posting to topic-based feeds (travel, culture, cost-of-living, academics, general)
3. Comments, upvotes/downvotes, reporting
4. Profanity filtering at the API layer + report queue
5. University profile pages with aggregated student posts

Out of scope (intentionally): notes uploads, teacher accounts, assignments, file storage, DMs, document-based verification.

## Repo Layout

```
campusvoice/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routers
│   │   ├── core/          # config, db, security
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # business logic (verification, moderation)
│   │   └── middleware/    # profanity filter, rate limit
│   ├── alembic/           # migrations (cursor generates)
│   ├── main.py
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # UI components
│   │   ├── lib/           # api client, utils
│   │   └── types/         # TS types
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.local.example
└── docker-compose.yml     # local Postgres + Redis
```

## Cursor Bootstrap Prompt

Paste this into Cursor (Composer or Agent mode) inside the empty repo to generate the rest:

> Generate the following boilerplate for a Next.js 15 + FastAPI project called CampusVoice. Repo structure is already laid out — see README.md.
>
> **Backend (`/backend`)**:
> - `pyproject.toml` using `uv` or `poetry` with deps: fastapi, uvicorn[standard], sqlalchemy[asyncio]>=2.0, asyncpg, alembic, pydantic>=2, pydantic-settings, python-jose[cryptography], passlib[bcrypt], redis>=5, better-profanity, email-validator, python-multipart, slowapi, httpx
> - `main.py` that instantiates FastAPI, mounts routers from `app/api/`, sets CORS for `http://localhost:3000`, registers the profanity middleware, and includes a `/health` endpoint
> - `app/core/config.py` using `pydantic-settings` to load DATABASE_URL, REDIS_URL, JWT_SECRET, JWT_ALGORITHM=HS256, ACCESS_TOKEN_EXPIRE_MINUTES=60*24*7, ALLOWED_EMAIL_DOMAINS (comma-separated list of university domains), SMTP_* vars
> - `app/core/db.py` with async SQLAlchemy engine + sessionmaker + `get_db` dependency
> - `app/core/security.py` with bcrypt password hashing, JWT encode/decode, `get_current_user` dependency that reads `Authorization: Bearer` and returns the User row
> - Alembic init with async support, pointed at `app/models/`
> - `.env.example` with all the keys above
>
> **Frontend (`/frontend`)**:
> - Next.js 15 with App Router, TypeScript, Tailwind, ESLint
> - Install: `@tanstack/react-query`, `zod`, `react-hook-form`, `@hookform/resolvers`, `lucide-react`, `clsx`, `tailwind-merge`, `class-variance-authority`, `js-cookie`, `@types/js-cookie`
> - Set up shadcn/ui (`button`, `input`, `card`, `badge`, `dropdown-menu`, `toast`, `dialog`, `tabs`, `textarea`)
> - `src/lib/api.ts` — typed fetch wrapper that reads JWT from cookie and adds `Authorization` header, throws on non-2xx
> - `src/lib/queryClient.ts` — React Query provider wrapper
> - `src/app/layout.tsx` — wraps app in QueryClientProvider + Toaster
> - `.env.local.example` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
>
> **Root**:
> - `docker-compose.yml` with `postgres:16-alpine` (port 5432) and `redis:7-alpine` (port 6379), named volumes, healthchecks
> - `.gitignore` for Python + Node + envs
> - `Makefile` with `dev-backend`, `dev-frontend`, `dev-db`, `migrate`, `migration name=...` targets
>
> Do NOT generate: SQLAlchemy models, Pydantic schemas, API routers, auth flow, profanity middleware, or any frontend pages/components — those are provided separately. Just the scaffolding above.

## Files Provided in This Repo (Cursor should NOT regenerate)

Everything under:
- `backend/app/models/`
- `backend/app/schemas/`
- `backend/app/api/`
- `backend/app/services/`
- `backend/app/middleware/`
- `frontend/src/app/(auth)/`
- `frontend/src/app/dashboard/`
- `frontend/src/components/`
- `frontend/src/types/`

## Local Dev

Project root: `~/achhiel`

```bash
# 1. Remove any stale containers, then spin up db + redis
cd ~/achhiel
docker rm -f campusvoice-redis campusvoice-postgres 2>/dev/null || true
docker compose up -d
# Postgres → port 5434, Redis → port 6379

# 2. Backend (new terminal)
cd ~/achhiel/backend
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --reload
# API: http://localhost:8000

# 3. Frontend (another terminal)
cd ~/achhiel/frontend
npm install
npm run dev
# UI: http://localhost:3000
```

## GDPR Notes

- Only store: email, hashed password, display name, university (derived from domain), country (optional, user-provided), created_at
- No ID documents stored at MVP
- Posts soft-deleted, hard-purged after 30 days
- User deletion cascades posts/comments
- Add a privacy policy page before launch
