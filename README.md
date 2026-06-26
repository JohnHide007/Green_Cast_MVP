# Green Cast — Portfolio Risk Intelligence

**Forward-looking, fully-attributable ESG & financial risk intelligence for European mid-market private equity, private credit, and real estate funds.**

Green Cast fuses three data streams — portfolio-company financials, ESG exposure metrics, and external macro/regulatory signals — into a single, auditable `RiskFactor` model. Deterministic rules compute the numbers; an LLM writes investor-ready commentary on top, with **every sentence traceable to the rule and data point that produced it**. The positioning is risk intelligence, not compliance reporting — compliance is a byproduct.

| | |
|---|---|
| **Live app** | https://green-cast-mvp-s613.vercel.app |
| **Live API** | https://green-cast-mvp.vercel.app ( `/docs` ) |
| **Stack** | FastAPI · SQLModel · Next.js 14 · TypeScript · Tailwind · Vercel AI Gateway |
| **Status** | Working MVP · deployed on Vercel (two projects, one repo) |

> **Demo data is synthetic.** The portfolio companies are invented for confidentiality, but they are scored against *real* EU regulatory anchors (EU ETS sector carbon intensities, EPC bands A–G, CBAM-covered sectors, realistic leverage/LTV ranges).

---

## The problem & the innovation

Mid-market funds dedicate **60–80 analyst hours per quarter** to consolidating portfolio-company spreadsheets, mapping them to regulatory templates, and rewriting commentary for LP reports and investment-committee memos. The output is backward-looking, expensive, and structurally unable to flag risk *before* it hits financials.

**The innovation:** a continuous, AI-driven risk intelligence layer that
1. **normalises** heterogeneous inputs into one canonical schema with visible data lineage,
2. **scores** them with a deterministic rules engine (transparent, not a black box), and
3. **narrates** the result with an attributed LLM commentary layer that drops straight into LP/IC documents.

The hybrid split — *rules for the math, AI for the narrative, attribution linking them* — is the answer to "is this a black box?": it isn't.

---

## Features

| Module | What it does | Type |
|---|---|---|
| **Unified schema + lineage** | Financials, ESG, and macro signals normalise into one `RiskFactor`; click any score to see its raw inputs and transform | Deterministic |
| **Rules engine** | Computes 0–100 risk factors and fires threshold alerts (leverage, carbon intensity, CBAM, LTV, …) | Deterministic |
| **AI Risk Commentary** | LLM turns the numbers + alerts into 4–6 attributed sentences for LP reports | **AI** |
| **AI Risk Interpretation** | LLM synthesises internal + external signals into a forward-looking risk thesis with ranked key risks | **AI** |
| **AI Data Normalisation** | Paste messy financial rows (Exact/SAP/Xero/Twinfield/Excel) → LLM maps them to the canonical schema | **AI** |
| **Pre-DD Screening** | Runs the same risk engine on prospective targets before acquisition | Deterministic |
| **ROI Calculator** | Quantifies analyst hours saved vs subscription cost; payback in < 1 quarter at default inputs | Deterministic |

All three AI features run through the **Vercel AI Gateway** and **degrade gracefully** — if no key is configured, the rules-based output still renders.

---

## Architecture

One Git repo, deployed as **two independent Vercel projects**:

```
Green_Cast_MVP/                      GitHub repo (public)
├── frontend/   -> Vercel project "green-cast-mvp-s613"   (Next.js, Root Dir = frontend)
└── backend/    -> Vercel project "green-cast-mvp"        (FastAPI, Root Dir = backend)
```

**Request flow**

```
Browser --> Next.js frontend --(same-origin /be/* rewrite)--> FastAPI backend --> SQLite (/tmp)
                                                                    |
                                                         AI calls   v
                                                         Vercel AI Gateway --> google/gemini-2.5-flash
```

Key decisions:

- **Same-origin API proxy.** The browser never calls the backend directly; `next.config.mjs` rewrites `/be/*` to the backend origin. This removes CORS entirely and avoids build-time URL pitfalls. Server components fetch the backend's absolute URL; the browser uses `/be`.
- **SQLite on serverless.** All data is derived from `seed.py`, so the DB is rebuilt into the writable `/tmp` directory on each cold start — correct because there is no user-persisted state. Graduating to Postgres (Neon/Supabase) is a connection-string change, no code rewrite.
- **Provider-agnostic AI.** A single `ai_gateway` client behind the OpenAI-compatible Gateway endpoint; swap models with one env var.

---

## Conceptual innovation -> code

| Pitch claim | Where it lives in code |
|---|---|
| "Everything maps to one schema" | `backend/app/models.py` -> `RiskFactor`; raw inputs normalise via `backend/app/normalization.py` |
| "Visible data lineage" | `RiskFactor.contributing_inputs` -> `/risk-factors/{id}/lineage` -> `frontend/components/risk-factor-card.tsx` drill-down |
| "Hybrid AI + rules, not a black box" | Rules: `backend/app/rules.py` · Narrative: `backend/app/commentary.py` · every sentence carries `source_refs` |
| "Forward-looking interpretation" | `backend/app/interpretation.py` (internal factors + alerts + macro -> thesis) |
| "AI normalisation engine" | `backend/app/ingestion.py` (messy rows -> canonical schema) |
| "Analyst-hour ROI" | `backend/app/routers/roi.py` + `frontend/components/roi-calculator.tsx` |

---

## AI integration (Vercel AI Gateway)

All AI runs through Vercel's native **AI Gateway** via its OpenAI-compatible endpoint, giving one API key, one billing/observability surface, and provider portability.

- **Client:** `backend/app/ai_gateway.py` — `openai` SDK pointed at `https://ai-gateway.vercel.sh/v1`.
- **Model:** `google/gemini-2.5-flash` by default (swap via `AI_MODEL`).
- **Resilience:** automatic retry-on-429 with backoff (handles free-tier throttling) and per-result caching (each company/input generated once).
- **Reasoning cap:** thinking-token budget is bounded so the model's reasoning can't exhaust the output budget and truncate JSON.
- **Graceful degradation:** no `AI_GATEWAY_API_KEY` -> endpoints return an "unavailable" flag, never a 500; rules-based scores still render.

---

## Project structure

```
Green_Cast_MVP/
├── README.md                <- you are here
├── AGENTS.md / CLAUDE.md    <- AI-agent orchestration instructions
├── CHANGELOG.md             <- development & collaboration history
├── backend/
│   ├── app/
│   │   ├── main.py          FastAPI app (lifespan: create + seed DB)
│   │   ├── database.py      engine; /tmp on Vercel
│   │   ├── models.py        SQLModel tables + response schemas
│   │   ├── normalization.py rules-based normalisation -> RiskFactor
│   │   ├── rules.py         threshold alert engine
│   │   ├── seed.py          synthetic, benchmark-anchored seed data
│   │   ├── ai_gateway.py    shared Vercel AI Gateway client (retry + JSON parsing)
│   │   ├── commentary.py    AI commentary (Module 5)
│   │   ├── interpretation.py AI risk interpretation (Module 4)
│   │   ├── ingestion.py     AI data normalisation (Module 1)
│   │   └── routers/         funds, portfolio, risk_factors, screening, roi, commentary, interpretation, ingestion
│   ├── tests/               112 pytest tests
│   ├── pyproject.toml       uv project ([tool.vercel] entrypoint)
│   ├── uv.lock              lockfile Vercel installs from
│   └── requirements.txt
└── frontend/
    ├── app/                 App Router pages: / · /funds · /funds/[id] · /portfolio/[id] · /screening · /roi · /ingestion
    ├── components/          nav, risk-factor-card, commentary-panel, interpretation-panel, holdings-table, roi-calculator
    ├── lib/                 utils.ts (apiFetch + /be proxy), types.ts
    └── next.config.mjs      /be/* -> backend rewrite
```

---

## Local development

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 18+, npm.

```bash
# Terminal 1 — backend (http://localhost:8000, docs at /docs)
cd backend
cp .env.example .env          # optional: add AI_GATEWAY_API_KEY for AI features
uv sync
uv run uvicorn app.main:app --reload

# Terminal 2 — frontend (http://localhost:3000)
cd frontend
npm install
npm run dev
```

The database seeds automatically on first run (30 companies across 3 funds). AI features work without a key — they just show "unavailable" until `AI_GATEWAY_API_KEY` is set.

---

## Environment variables

**Backend** (`backend/.env` locally; Vercel env vars in production)

| Key | Required | Purpose |
|---|---|---|
| `AI_GATEWAY_API_KEY` | for AI features | Vercel AI Gateway key (Dashboard -> AI Gateway -> API Keys) |
| `AI_MODEL` | no | Model slug, default `google/gemini-2.5-flash` |
| `DATABASE_URL` | no | Defaults to `./greencast.db` locally, `/tmp/greencast.db` on Vercel |

**Frontend** — none required in production; the backend URL is configured in `next.config.mjs` (`/be` proxy target).

---

## Deployment

Both apps deploy from this repo via Vercel's GitHub integration.

**Backend** (`green-cast-mvp`): Root Directory `backend`, Python 3.12 (`.python-version`), entrypoint `app.main:app` (`[tool.vercel]` in `pyproject.toml`). Dependencies install from `uv.lock`. Set `AI_GATEWAY_API_KEY` in project env vars. Deployment Protection is off so the API is publicly reachable.

**Frontend** (`green-cast-mvp-s613`): Root Directory `frontend`, framework auto-detected (Next.js). The `/be/*` rewrite proxies to the backend, so no CORS configuration is needed.

Pushing to `main` auto-redeploys both projects.

---

## Testing

```bash
cd backend
uv run pytest -q          # 112 tests
```

Tests cover the rules engine, normalisation, ROI, screening, and the AI endpoints (graceful-degradation + mocked-gateway paths, so no live API calls or keys are needed in CI). The frontend is type-checked with `npx tsc --noEmit`.

---

## AI agent orchestration

This repository was built with AI coding agents. Agent-facing instructions live in **AGENTS.md** (universal) and **CLAUDE.md** (Claude Code), covering conventions, golden rules (e.g. never call the live AI in tests; preserve the attribution contract; keep the rules-vs-AI split honest), commands, and how work is divided across agents.

---

## Development history

The full commit history is the collaboration record; **CHANGELOG.md** summarises the phases: core MVP -> Vercel migration -> AI Gateway integration -> resilience & feature build-out.

---

*Green Cast is a risk-intelligence platform. Regulatory compliance is a byproduct, not the primary output.*
