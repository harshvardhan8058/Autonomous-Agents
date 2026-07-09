# Autonomous AI Agent

A single-agent system that takes a natural-language request, generates its own execution
plan, executes each task, reviews its own output (Reflection + Self-Check), and delivers
a professionally formatted DOCX report.

## Architecture

```
backend/
  main.py                     FastAPI entrypoint
  app/
    api/routes.py             POST /agent · GET /documents/{id} · GET /health
    core/config.py            env-driven settings, provider resolution
    core/llm.py               handwritten async LLM client (httpx), JSON retry
    agent/orchestrator.py     pipeline sequencing only
    planner/planner.py        request → structured Plan (goal/assumptions/tasks/confidence)
    executor/executor.py      sequential task execution with state tracking
    reflection/reflector.py   self-review + one bounded improvement pass
    tools/                    dates · titles · timeline (only tools actually used)
    documents/docx_generator.py  DOCX rendering (python-docx)
    schemas/models.py         Pydantic contracts
    services/document_store.py   id → file mapping, path-traversal safe
    utils/json_utils.py       tolerant JSON extraction
frontend/                     React + Vite + Tailwind v4 (dark, glassmorphism)
vercel.json                   multi-service routing (frontend "/", backend "/api")
```

## Flow

```
User Request → Planner → Task List → Executor → Reflection → DOCX Generator → Response
```

- **Planner** — LLM decomposes the request into 3–8 ordered tasks, each mapping to one report section. Structured JSON, validated with Pydantic. No hardcoded task lists.
- **Executor** — runs tasks sequentially, passing already-written headings as context for consistency. Per-task status and duration are tracked.
- **Reflection (mandatory improvement)** — a strict self-review scores completeness, consistency, and formatting. If quality is below threshold, exactly **one** improvement pass rewrites the flagged sections (capped at 3). Never loops.
- **DOCX Generator** — heading hierarchy, TOC field, executive summary, timeline table, bullet lists, styled footer, generated timestamp.

## Features

- Single-agent architecture — no unnecessary agent frameworks; every module handwritten
- Structured errors: 502 for provider/JSON failures, 503 for missing credentials, 404 for unknown documents
- Malformed LLM JSON retried exactly once with a repair prompt
- Document IDs validated against a strict pattern (no path traversal)
- Premium dark UI with live workflow visualization and DOCX download

## Setup

**LLM credentials** (either works):

- `GROQ_API_KEY` — calls Groq directly (`llama-3.3-70b-versatile`)
- `AI_GATEWAY_API_KEY` — routes the same Groq model through Vercel AI Gateway

**Local development**

```bash
# backend
cd backend && pip install -r ../requirements.txt
fastapi dev main.py --port 8000

# frontend
cd frontend && pnpm install && pnpm dev
```

On Vercel, `vercel.json` runs both services and routes `/api/*` to the backend automatically.

## API

| Method | Path                  | Description                                    |
| ------ | --------------------- | ---------------------------------------------- |
| POST   | `/api/agent`          | `{"request": "..."}` → plan, summary, doc link |
| GET    | `/api/documents/{id}` | Download the generated DOCX                    |
| GET    | `/api/health`         | Liveness check                                 |

Example:

```bash
curl -X POST /api/agent -H "Content-Type: application/json" \
  -d '{"request":"Create a technical proposal for migrating a monolith to microservices"}'
```

## Screenshots

> _Placeholder: landing view with workflow rail_
>
> _Placeholder: generated plan + execution progress_
>
> _Placeholder: reflection report + download_

## Tradeoffs

- **Synchronous pipeline** — one request returns the full result. Simple to reason about and demo; streaming/SSE progress would be the next iteration.
- **Filesystem document store** — no database per requirements; documents are ephemeral on serverless. A blob store would be the production choice.
- **One reflection pass** — bounded self-correction captures most quality gains without token-burning loops.
- **No LangChain** — a ~50-line httpx client is easier to debug, test, and reason about than framework abstractions for a single-provider pipeline.
