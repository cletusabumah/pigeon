# Pigeon

We're building Pigeon — a chess scoresheet scanner and **lifelong game archive**. It turns handwritten tournament notation into clean PGN files, organizes every game by event, and gives players, coaches, and organizers tools to review, stats-track, and preserve games that would otherwise be forgotten—especially games from lower sections and chessmats that never reach FIDE or public databases.

## Why It Matters

Most over-the-board games are written on paper and then disappear. Top boards sometimes get recorded; everyone else loses valuable history. With Pigeon, players save **all** their games—NC Opens 2024, Mombasa Opens, club nights—in one place with dashboard stats, replay, and coach/organizer workflows.

## Why We Will Win

- **Faster scanning** than manual entry and clunky one-off tools.
- **Event-organized archive** for your entire chess life, not single-game exports.
- **Personal dashboard**: openings, win rates, streaks, top rivals.
- **Coach tools**: student permission, stars, comments on games.
- **Organizer bulk workflow**: phone scan → laptop review with AI legality hints.
- **Every handwriting level** with smart correction UX—we don't pretend OCR is perfect.

See [`docs/differentiation.md`](docs/differentiation.md) for our full competitive story.

## Our First Goal (September)

We are shipping a functional, deployed app that:

- Uploads or captures scoresheet images.
- Extracts move notation with uncertainty flags.
- Lets users correct moves quickly with the image visible.
- Validates moves against chess rules.
- Exports clean PGN.
- Saves games in event-grouped, searchable libraries.
- Shows dashboard stats and in-app replay.
- Supports user accounts with security basics.

## Team

**Alex Mutua** (founder, 60%) · **Cletus Abumah** (co-founder, 40%) — CS freshmen, ~20 hrs/week each.

Our primary goal: **internship-ready engineering** at companies like Microsoft, Meta, and similar programs. See [`docs/team-and-equity.md`](docs/team-and-equity.md).

## Weekly todos

We track tasks in JSON and mark them from the terminal:

```bash
pdone who alex      # once per machine (see docs/todos.md)
pdone git-init        # mark a task done → Alex: 1/5 done
```

See [`docs/todos.md`](docs/todos.md).

## Documentation

Full index: [`docs/README.md`](docs/README.md)

| File | What it covers |
|------|----------------|
| [`docs/master-plan.md`](docs/master-plan.md) | **Main plan** — every step, week by week |
| [`docs/differentiation.md`](docs/differentiation.md) | Why we win (archive, dashboard, coaches, organizers) |
| [`docs/product-features.md`](docs/product-features.md) | Full feature list by player / coach / organizer |
| [`docs/team-and-equity.md`](docs/team-and-equity.md) | Roles, 60/40 split, internship goals |
| [`docs/vision.md`](docs/vision.md) | Our mission (every board, not just top sections) |
| [`docs/mvp-spec.md`](docs/mvp-spec.md) | September must-haves vs stretch |
| [`docs/roadmap.md`](docs/roadmap.md) | High-level phases |
| [`docs/team-workflow.md`](docs/team-workflow.md) | How we work — git, PRs, weekly rhythm |
| [`docs/todos.md`](docs/todos.md) | Weekly JSON todos + `pdone` command |
| [`docs/privacy-security.md`](docs/privacy-security.md) | Security rules from day one |
| [`docs/github-access.md`](docs/github-access.md) | 2FA + branch protection checklist |
| [`docs/what_we_learned.md`](docs/what_we_learned.md) | Weekly log — what we did and learned |
| [`docs/wireframes.md`](docs/wireframes.md) | Screen layout sketches |
| [`docs/ocr-strategy.md`](docs/ocr-strategy.md) | OCR engine choice and testing plan |
| [`docs/phase-1-tickets.md`](docs/phase-1-tickets.md) | Phase 1 GitHub issues / build order |
| [`docs/test-data-protocol.md`](docs/test-data-protocol.md) | Consent rules for scoresheet test images |

## Our Stack

We chose a **Python backend + React frontend + SQL database** split so each founder can own their lane while sharing one API contract.

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | React + Vite | Fast dev server, component ecosystem, Alex owns UI |
| Backend | FastAPI (Python) | Async APIs, Pydantic validation, matches our Python coursework |
| Database | SQLite (dev) → Postgres (staging) | Zero setup locally; standard managed Postgres in production |
| OCR (Phase 1) | Tesseract + OpenCV | Free, runs locally, swappable via `OcrProvider` — see [`docs/ocr-strategy.md`](docs/ocr-strategy.md) |
| Chess logic | python-chess | PGN export and move legality validation |

**Why not a monolith or Next.js full-stack?** We want clear boundaries: Cletus ships upload/OCR/review APIs; Alex ships capture, correction UX, and auth UI. FastAPI + React is the same pattern used at many internship-target companies (separate services, OpenAPI docs, CI per layer).

**Why Tesseract first?** Handwriting OCR is hard; Phase 1 proves the pipeline (upload → process → raw text → human correction) without cloud cost or API keys. Cloud OCR (Google Vision, etc.) stays behind the same `OcrProvider` interface for hard sheets later.

## Project layout

```
pigeon/
├── backend/           # FastAPI (Cletus — Week 1 scaffold)
├── frontend/          # React + Vite (Alex)
├── docs/              # Plans, specs, protocols
├── scripts/           # pdone, setup-shell.sh
├── test-fixtures/     # Synthetic/consented scoresheets only
├── todos/             # Weekly task JSON (week-01.json, …)
└── README.md
```

## Development setup

### Prerequisites

- **Node.js** 18+ (`node -v`, `npm -v`)
- **Python** 3.11+ (`python3 -v`)
- **Git** + GitHub access — see [`docs/github-access.md`](docs/github-access.md) for 2FA and branch protection
- **Tesseract** (for local OCR testing): `brew install tesseract` on macOS

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173/**

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # OCR_PROVIDER=mock by default; use tesseract after brew install
alembic upgrade head   # create the database from migrations
uvicorn app.main:app --reload
```

API runs at **http://localhost:8000** — try **http://localhost:8000/health**

#### Database (Phase 2 schema)

Alembic migrations live in `backend/alembic/versions/`. A fresh clone should always run `alembic upgrade head` before starting the server.

| Table | Purpose |
|-------|---------|
| `events` | Tournaments (name, location, section, dates) |
| `players` | White/black player names and optional rating IDs |
| `games` | Game metadata, `event_id` FK, and verified `pgn` text |
| `game_moves` | Parsed/corrected moves per ply |
| `scoresheet_uploads` | Uploaded image path + OCR status/raw JSON |

**Not in Phase 2:** `users` and per-account isolation — planned for Phase 3 (ticket 3.1). Auth is local-dev only until then.

For PostgreSQL (staging/production), set `DATABASE_URL` in `.env` to the `postgresql+asyncpg://…` URL from `.env.example`, then run `alembic upgrade head` against that database.

To run the optional local Postgres migration test (requires a running Postgres instance):

```bash
RUN_POSTGRES_MIGRATION_TEST=1 DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chess_archive \
  pytest tests/test_migrations.py::test_migrations_upgrade_downgrade_roundtrip_postgres -v
```

CI runs this automatically in the `migrations-postgres` job on every pull request.

**OCR spike (local):** set `OCR_PROVIDER=tesseract` in `backend/.env`, then:

```bash
# Upload a JPEG/PNG scoresheet
curl -X POST "http://127.0.0.1:8000/api/v1/uploads" -F "file=@/path/to/sheet.png"

# Process — returns raw_text and lines (handwriting quality varies)
curl -X POST "http://127.0.0.1:8000/api/v1/uploads/{UPLOAD_ID}/process"
```

CI and pytest use `OCR_PROVIDER=mock` so Tesseract is not required in GitHub Actions.

### Weekly todos

```bash
./scripts/setup-shell.sh   # once — adds pdone to ~/.zshrc
pdone who alex             # or: pdone who cletus
pdone status
```

See [`docs/todos.md`](docs/todos.md).

## Status

**Week 2 (Phase 1)** — upload API merged; OCR spike on `feature/ocr-spike` (Tesseract + raw text on process). Next: Alex wires upload UI + Vite proxy to the API.

See [`docs/merge-recovery.md`](docs/merge-recovery.md) if git ever feels confusing.

## Long-Term Vision

We want Pigeon to become the default archive for over-the-board chess: every section, every board, every game—preserved, searchable, and useful for players, coaches, and tournament organizers worldwide.
