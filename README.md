# Green Cast — Portfolio Risk Intelligence

Forward-looking ESG-financial risk monitoring for European mid-market PE, private credit, and real estate funds.

---

## One-command local run

```bash
# Terminal 1 — backend (port 8000)
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2 — frontend (port 3000)
cd frontend
npm run dev
```

App: http://localhost:3000 · API docs: http://localhost:8000/docs

---

## Setup

### Backend

```bash
cd backend
cp .env.example .env          # optional: add ANTHROPIC_API_KEY for AI commentary
uv sync                       # install dependencies
uv run pytest tests/ -q       # 108 tests, all green
uv run uvicorn app.main:app --reload
```

Database seeds automatically on first run (30 companies across 3 funds).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | No | Enables AI commentary on company risk pages. Without it, the rules-based scores still work; commentary shows "unavailable" state. |

---

## Demo script (recording)

### Money shot 1 — Portfolio overview
1. Open http://localhost:3000/funds
2. Three fund cards visible: Nordkap (PC), Rhein (RE), Albion (PE)
3. Click **Nordkap Private Credit I**
4. Holdings table loads with risk scores; **Hanseatic Steel** is clearly **HIGH** (score ~75+)

### Money shot 2 — Company drill-down + data lineage
1. Click **Hanseatic Steel GmbH**
2. Overall Risk Score headline: `HIGH` in red badge
3. Sub-composites: Transition Risk + Financial Risk both elevated
4. Click **Leverage (Net Debt / EBITDA)** card → lineage expands
5. Show: raw net_debt €250M, annualised EBITDA €36.4M, **6.9× leverage**, transform formula
6. Click **CBAM Exposure** → CBAM Regulation 2023/956 source reference
7. Risk alerts sidebar: `LEVERAGE_HIGH`, `CARBON_INTENSITY_HIGH`, `CBAM_HIGH_EXPOSURE`
8. Click **Generate commentary** → 4–6 attributed sentences; click **Show sources** toggle

> Talking point: "Every sentence cites the rule or factor that produced it — same engine, audit trail from raw input to narrative."

### Money shot 3 — Pre-investment screening
1. Click **Pre-DD Screening** in nav
2. Enter target: carbon 320, energy 0.78, supplier 0.65, CBAM high, net_debt 300, EBITDA 8, revenue 40
3. Click **Run screening** → verdict loads
4. Show RAG badge (RED), transition + financial sub-scores, top 3 risk drivers
5. Alerts: `CARBON_INTENSITY_HIGH`, `CBAM_HIGH_EXPOSURE`, `LEVERAGE_HIGH`

> Talking point: "Same normalization engine as monitoring — analyst sees the same risk view pre- and post-acquisition."

### Money shot 4 — ROI calculator
1. Click **ROI Calculator** in nav
2. Defaults: 25 companies, 12 hrs/report, 4×/year, €120/hr, Growth tier
3. Click **Calculate ROI**
4. Headline: **2.5 months** payback
5. Show table: 960 hrs saved · €115,200 annual saving · €24,000 cost · €91,200 net

---

## Architecture justifications

**Why Python + FastAPI (not Node)?**  
Numerical normalization and rules logic are cleaner in Python; SQLModel gives typed SQLite with zero boilerplate. WeasyPrint PDF generation is first-class.

**Why SQLite (not Postgres)?**  
30-company demo; one-command setup with no Docker dependency. Schema is identical to Postgres via SQLModel — migration trivial.

**Why Next.js 14 App Router?**  
Server components + `force-dynamic` means zero hydration cost for data-heavy pages. Co-located data fetching keeps the component tree simple.

**Why Claude for commentary?**  
Hybrid approach: deterministic rules fire first (auditable, always-on), then Claude receives only the computed metrics and alert identifiers. Every sentence must cite a source ref — hallucination risk is bounded.

**Why WeasyPrint?**  
HTML/CSS → PDF with full Green Cast brand fidelity, no Puppeteer/headless-Chrome overhead.

---

## Recording notes

- Resolution: 1080p minimum
- Browser zoom: 100% in Chrome/Arc
- Quit Slack/notifications before recording
- Test all API calls with backend running before pressing record
- Lineage card expand animation is ~200ms — pause briefly before speaking

