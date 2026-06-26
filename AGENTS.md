# AGENTS.md — Orchestration for AI coding agents

This is the universal agent guide for the Green Cast repository. It is read by
Claude Code, Cursor, Codex, Gemini and other agents. `CLAUDE.md` points here.

## What this project is

Green Cast is a portfolio risk-intelligence MVP for European mid-market funds.
- **Backend:** FastAPI + SQLModel (SQLite), Python 3.12, managed with `uv`. Deployed on Vercel (`green-cast-mvp`).
- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind. Deployed on Vercel (`green-cast-mvp-s613`).
- **AI:** three features (commentary, interpretation, normalisation) routed through the Vercel AI Gateway via `backend/app/ai_gateway.py`.

Read `README.md` first for the full architecture.

## Golden rules (do not break these)

1. **Keep the rules-vs-AI split honest.** Deterministic numbers live in `rules.py` / `normalization.py`. The LLM only writes narrative. Never present rules output as "AI", and never let the LLM invent numbers.
2. **Preserve the attribution contract.** Every commentary sentence and every interpreted risk must carry `source_refs` pointing at a real factor/rule/signal id. UI relies on this for the "Show sources" toggle.
3. **AI must degrade gracefully.** If `AI_GATEWAY_API_KEY` is missing or a call fails, return an `available: false` response with a message — never a 500.
4. **Never call the live AI in tests.** Tests mock `app.ai_gateway` (`is_configured`, `chat_json`). Keep them offline and deterministic.
5. **The browser never calls the backend directly.** Client fetches go through the same-origin `/be` proxy (`next.config.mjs` + `lib/utils.ts`). Don't reintroduce `NEXT_PUBLIC_API_URL` direct calls or CORS coupling.
6. **Dependencies install from `uv.lock` on Vercel.** If you change `pyproject.toml` deps, regenerate `uv.lock` (`uv lock`) or the deploy installs the wrong packages.
7. **SQLite path is env-driven.** `/tmp` on Vercel (read-only filesystem elsewhere). Don't hardcode a writable path.

## Commands

```bash
# Backend
cd backend && uv sync
uv run uvicorn app.main:app --reload      # dev server :8000
uv run pytest -q                          # 112 tests — must stay green

# Frontend
cd frontend && npm install
npm run dev                               # dev server :3000
npx tsc --noEmit                          # type-check before committing
```

## Definition of done

- `uv run pytest -q` passes (backend).
- `npx tsc --noEmit` passes (frontend).
- AI changes verified on both paths: no-key fallback AND mocked-gateway success.
- No secrets committed; `.env` stays local.

## How we orchestrate agents

We use a small, role-based fleet rather than one agent doing everything:

- **Claude Code (primary build + deploy agent).** Owns multi-file features, the FastAPI/Next.js wiring, the Vercel migration and deployment debugging, and writing tests. Best at long, multi-step tasks that span the whole repo and at reading build/runtime logs to diagnose failures.
- **Inline editor agents (Cursor / Copilot).** Used for small, local edits — single-component tweaks, prop changes, styling — where a full repo agent is overkill.
- **Review pass.** Before a risky change is merged, a separate agent session reviews the diff against the golden rules above (especially the attribution contract and the no-live-AI-in-tests rule).

Division of labour mirrors the human owners: one track focuses on the data/rules/AI backend, the other on the UX/landing/investor-facing frontend, with the README + this file as the shared contract that keeps both consistent.

## File map (where to work)

| Area | Files |
|---|---|
| Risk schema & scoring | `backend/app/models.py`, `normalization.py`, `rules.py`, `seed.py` |
| AI layer | `backend/app/ai_gateway.py`, `commentary.py`, `interpretation.py`, `ingestion.py` |
| API routes | `backend/app/routers/*.py` |
| Frontend pages | `frontend/app/**/page.tsx` |
| Frontend components | `frontend/components/*.tsx` |
| API client + proxy | `frontend/lib/utils.ts`, `frontend/next.config.mjs` |
