# Changelog & collaboration history

The Git commit history is the authoritative collaboration record. This document
summarises the development in phases so the build journey is readable at a glance.

The team divided work along the same lines as the pitch: one track owned the
data / rules / AI **backend**, the other owned the **frontend** and the
investor-facing experience, with `README.md` and `AGENTS.md` as the shared contract.

---

## Phase 1 — Core MVP (`V1`)

The conceptual innovation, in code:
- Canonical `RiskFactor` schema with three raw input types (`FinancialRecord`, `ESGMetric`, `MacroSignal`) and visible data lineage.
- Deterministic normalisation + rules engine (0–100 scores, threshold alerts).
- AI commentary layer with per-sentence attribution.
- Synthetic, benchmark-anchored seed data (30 companies across 3 funds).
- Frontend: portfolio monitoring, lineage drill-down, pre-DD screening, ROI calculator.
- Full pytest suite.

## Phase 2 — Vercel migration (`Vercel reformation` → `frontend vercel bug fix`)

Moving from local dev to a deployed product:
- Backend converted to the Vercel Python runtime (Python 3.12, `uv.lock`, `[tool.vercel]` entrypoint, `/tmp` SQLite, removed unused WeasyPrint).
- Frontend deployed as a second Vercel project (Root Directory = `frontend`).
- Resolved the Python-version build failure (3.11 → 3.12) and a `.gitignore` rule that was hiding `frontend/lib/`.

## Phase 3 — Provider-agnostic AI via Vercel AI Gateway (`ai gateway api fix` → `ai back and front end connection`)

- Replaced the direct Anthropic client with a single `ai_gateway` client behind the **Vercel AI Gateway** (OpenAI-compatible endpoint), defaulting to `google/gemini-2.5-flash`.
- Added two new AI modules — **risk interpretation** and **AI data normalisation** — plus their routers and UI panels.
- Regenerated `uv.lock` so Vercel installs `openai` (the lockfile, not `requirements.txt`, is the source of truth on Vercel).

## Phase 4 — Connectivity & resilience (`bug fix` → `Add 429 retry with backoff + result caching`)

- Introduced the **same-origin `/be` proxy** so the browser never calls the backend directly — eliminating CORS and the `localhost` fallback that broke client-side calls.
- Surfaced real AI errors instead of cryptic `NoneType` failures.
- Added **retry-on-429 with backoff** and **per-result caching** to absorb free-tier rate limits.
- Capped the model's reasoning-token budget so "thinking" can't truncate the JSON output.

## Phase 5 — Investor-facing build-out (`Add landing sections…` → `Restyle impact stats…`)

- Landing page: impact statistics, a "why funds use it" value-prop section, an embedded ROI calculator, and a buyer-oriented FAQ.
- Portfolio holdings table: filter by risk rating / sector and click-to-sort columns.
- Clean card-based visual design across the landing sections.

---

### Conventions going forward

- Each change keeps `uv run pytest -q` (112 tests) and `npx tsc --noEmit` green.
- Commits are scoped and descriptive; pushing to `main` auto-deploys both Vercel projects.
