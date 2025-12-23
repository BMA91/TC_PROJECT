# TC_PROJECT

## Project Overview

TC_PROJECT is a small full-stack system composed of three main parts:

- Backend: FastAPI application implementing REST endpoints for users, tickets and admin tasks.
- Frontend: A Next.js (React) app that serves the user interface.
- AI services: A collection of scripts and services under `ai/` used for document ingestion, vector search (Chroma), and LLM-based solution composition.

This README explains the architecture, how the pieces interact, and provides the exact commands to run the project locally on Windows.

## Architecture (high level)

- Frontend (`front_end`) — Next.js app (Next 16, React 19). Runs on port 3000 in development by default.
- Backend (`backend/app`) — FastAPI app using SQLAlchemy and a local SQLite database `database.db`. Runs on port 8000 in development by default.
- AI services (`ai`) — Helper scripts and modules for ingesting PDFs, building a Chroma vector DB, and composing LLM responses. It uses `chromadb` and transformer/LLM packages.

Interaction flow:

1. User interacts with the UI served by the Next.js frontend.
2. Frontend calls the FastAPI backend endpoints (e.g., `/users`, `/tickets`).
3. Backend handles auth, persistence, and may call into `ai/` modules or services to perform vector-search/LLM tasks.
4. AI modules persist vector data in `ai/chroma_db` and use models configured in `ai/requirements.txt`.

## Key files & locations

- Backend entrypoint: `backend/app/main.py`
- Backend DB config: `backend/app/database.py` (uses `sqlite:///./database.db` by default)
- Backend requirements: `backend/requirements.txt`
- Frontend app: `front_end` (see `front_end/package.json`)
- AI helper scripts: `ai/*.py` and `ai/requirements.txt`

Default admin credentials (created on backend startup for development):
- email: `admin@gmail.com`
- password: `admin`

> Note: On startup `backend/app/main.py` recreates DB tables (development mode). In production, replace this with migrations (Alembic) and remove automatic drop/create.

## Prerequisites

- Node.js (recommended v18+), npm
- Python 3.11 (or >=3.10)
- Git (optional)

Windows-specific notes: these commands below are PowerShell-style. For WSL/Linux/macOS, use the same commands but with bash-compatible syntax.

## Setup & Run (development)

1) Frontend

Open PowerShell and run:

```powershell
cd C:\Users\PC\Desktop\Studies\TC_PROJECT\front_end
npm install
npm run dev
```

Alternative (run from repo root):

```powershell
npm --prefix front_end run dev
```

By default the dev server runs at http://localhost:3000

2) Backend

Create and activate a Python virtual environment, install requirements, and run uvicorn:

```powershell
cd C:\Users\PC\Desktop\Studies\TC_PROJECT\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell activation
pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Quick single-line (from repo root) to run backend in PowerShell:

```powershell
cd backend; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

By default the backend API will be available at http://localhost:8000 and includes a root health route `/`.

3) AI services (optional, used by backend/features)

Create a separate virtual environment (recommended) and install AI requirements:

```powershell
cd C:\Users\PC\Desktop\Studies\TC_PROJECT\ai
python -m venv .venv-ai
.\.venv-ai\Scripts\Activate.ps1
pip install -r requirements.txt
```

Many AI packages require substantial native dependencies and GPU support; consult `ai/requirements.txt` and your environment if you plan to run large LLMs locally.

## Production / Build

To build the frontend for production and run the optimized Next.js server:

```powershell
cd C:\Users\PC\Desktop\Studies\TC_PROJECT\front_end
npm install
npm run build
npm run start
```

For backend production deployments:
- Replace the development DB recreation in `backend/app/main.py` with proper migrations.
- Use a production ASGI server (uvicorn/gunicorn with workers) and configure environment variables.

## Environment variables & config

- The backend uses `backend/app/database.py` which defaults to `sqlite:///./database.db`.
- If you need to configure a different DB, set `DATABASE_URL` in your environment or modify `database.py` to read from `.env`.
- The project contains `python-dotenv` in requirements; you can add a `.env` file under `backend/` and load it from `app/main.py` or `database.py` before engine creation.

## Troubleshooting

- Error: `ENOENT: no such file or directory, open '.../package.json'` — make sure you run `npm run dev` inside `front_end` or use `npm --prefix front_end run dev`.
- Backend recreates DB on startup: development behavior; to persist data across restarts, remove the `drop_all` call in `app/main.py` or use migrations.
- If AI packages fail to install: ensure correct Python version, install `pip` build tools, and consider using a conda env for heavy ML dependencies.

## Useful commands summary

PowerShell (development):

```powershell
# Start frontend (dev)
cd front_end
npm install
npm run dev

# Start backend (dev)
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start AI env (optional)
cd ai
python -m venv .venv-ai
.\.venv-ai\Scripts\Activate.ps1
pip install -r requirements.txt
```

From repo root (single-line alternatives):

```powershell
npm --prefix front_end run dev
# and
cd backend; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Next steps / Recommendations

- Add a `.env` for configurable settings and update `database.py` to read from it.
- Replace DB recreation with database migrations (Alembic) for production.
- Add documentation for AI model configuration (which LLM provider or local model to use).

---

If you want, I can:
- Add `.env.example` and update `database.py` to read `DATABASE_URL` from env.
- Add a short `Makefile` or PowerShell script to start both backend and frontend concurrently.

