# Green Cast — Demo Video Script

**FinTech Assignment 2 · target length: under 10 minutes · two presenters: Hidde & Zhen**

Easy-English script. Short sentences, simple words, made to be read out loud.
`[screen: …]` lines tell you what to show. Time cues are a guide.

Covers the five required points:
1. Main features · 2. Architecture + innovation→code (+ UX) · 3. Deployment + product demo · 4. Investor oriented · 5. Coding agents + orchestration. Plus scaling, operations, and security at the end.

---

## 0:00 – 0:40 · The problem — **Hidde**

> Hi, we are Hidde and Zhen, and this is **Green Cast**.
>
> Today, mid-market investment funds spend a lot of time on risk reporting. A typical fund spends **60 to 80 analyst hours every quarter**. People copy numbers from many spreadsheets by hand. They map them to rules. Then they write the same commentary again and again for their investors.
>
> This work is slow, expensive, and it looks backward. It tells you what already happened. It does not warn you early.
>
> Green Cast fixes this. It is a risk-intelligence platform for private equity, private credit, and real estate funds in Europe.

*[screen: the landing page hero of https://green-cast-mvp-s613.vercel.app]*

---

## 0:40 – 1:20 · The solution and main features — **Zhen**

> Green Cast does three things in one place.
>
> First, it takes three kinds of data — company **financials**, **ESG** data, and outside **market and regulation** signals — and puts them into one simple model.
>
> Second, it scores the risk with clear rules. Not a black box.
>
> Third, an **AI** writes the report text on top. And every sentence shows where it came from.
>
> So the main features are: one unified risk score, full data lineage, AI commentary, AI interpretation, AI data cleaning, pre-deal screening, and an ROI calculator. Let us show you.

*[screen: scroll the landing page — impact stats, "why funds use it", FAQ]*

---

## 1:20 – 4:20 · Live product demo

### Portfolio monitoring & lineage — **Hidde**
> Here is the portfolio. We have three funds across the three strategies.

*[screen: click "Portfolio" → open a fund]*

> Each company gets a risk score from 0 to 100. I can **filter** by risk level or sector, and **sort** by any column. Let me sort by risk score, highest first.

*[screen: use the filter chips and click the "Risk Score" column header]*

> Now the most important question for an investor: can you trust the score? Yes — because you can open it. I click one company, then click any factor.

*[screen: open a company → click a risk factor to expand the lineage drawer]*

> This shows the exact raw input, the source table, and the formula. This is our core idea: **everything maps to one schema, and you can always see why.**

### AI commentary — **Hidde**
> Now the AI part. I press "Generate commentary".

*[screen: click "Generate commentary" on the company page]*

> The AI writes a short, professional risk note. And look — I turn on **"Show sources"**. Every sentence is tagged with the rule or data point behind it. The numbers come from our rules. The AI only writes the words. That is our hybrid design.

*[screen: toggle "Show sources"]*

### AI interpretation — **Zhen**
> Next is the interpretation. This goes one step further.

*[screen: click "Generate interpretation"]*

> It mixes the inside data with outside signals, like interest rates and CBAM carbon rules, and gives a forward-looking risk view with the top risks ranked. This is the part that saves the most analyst time.

### AI data cleaning — **Zhen**
> Onboarding a new company is usually painful, because every company sends data in a different format. Watch this.

*[screen: open "AI Normalise", paste the example messy Dutch "Exact" rows, click "Normalise with AI"]*

> I paste messy financial rows in Dutch — "Boekjaar", "Omzet", "Nettoschuld". The AI maps them to our clean schema by itself. No custom code per system. This is what makes onboarding take days, not weeks.

### Screening & ROI — **Zhen**
> Two more quick things. **Pre-deal screening** runs the same engine on a company you do not own yet, before you buy.

*[screen: open "Pre-DD Screening", run one]*

> And the **ROI calculator** shows the money. At default numbers, a mid-market fund pays back the cost in under one quarter.

*[screen: open ROI calculator, click "Calculate ROI", show payback]*

---

## 4:20 – 6:00 · Architecture and innovation in code — **Hidde**

> Let us show how this works under the hood, and how our idea becomes code.

*[screen: simple architecture diagram or the README architecture section]*

> We have two parts. A **FastAPI** backend in Python, and a **Next.js** frontend in TypeScript. They live in one repository but deploy as two services.
>
> Our main idea — "one schema with lineage" — is one model in the code called `RiskFactor`. Every raw input normalises into it, and each score keeps a pointer back to its source. That pointer is exactly what you saw in the drill-down.
>
> The "rules plus AI" idea is also split in code. One file does the math with fixed rules. Another file calls the AI for the text. The link between them is the source tag on every sentence.
>
> For the user experience, the design is calm and clean. Risk is color-coded — green, amber, red. Heavy work, like the AI, only runs when you click a button, so pages stay fast. And if the AI is ever off, the rule-based scores still show. The product never breaks.

---

## 6:00 – 6:50 · Deployment — how it is built and used — **Hidde**

> Deployment is simple and modern. We push our code to GitHub, and **Vercel** builds and ships both services automatically.

*[screen: the live URL in the browser address bar / Vercel dashboard, optional]*

> The frontend talks to the backend through a same-origin proxy, so there are no CORS problems. All the AI runs through the **Vercel AI Gateway**. That gives us one key, one bill, and the freedom to switch the AI model with a single setting. Right now we use Google Gemini Flash, which is fast and very cheap.
>
> To use the product, a fund just opens the web app. There is nothing to install.

---

## 6:50 – 8:10 · The investor case — **Zhen**

> Now, why is this a good business?
>
> The market is large and growing. Private credit alone is about **1.6 trillion dollars** and is set to triple by 2029. At the same time, EU rules like CSRD and SFDR keep getting heavier, faster than funds can hire.
>
> Our customers are the **mid-market funds**, under two billion euro. Big tools like MSCI and Sustainalytics are built for giant funds and are too expensive and too slow for this group. We are built only for them.
>
> Our revenue model is simple **SaaS subscription**, priced by portfolio size, with onboarding and API access on top. Because our AI cleaning makes adding a company almost free for us, we can serve this market and still make good margins.
>
> Around 63% of firms already use or plan to use AI for ESG. The funds that build this intelligence layer now will be the standard later. That is our opportunity.

---

## 8:10 – 9:05 · Coding agents and orchestration — **Hidde**

> The assignment asks which AI coding agents we used. We built Green Cast mainly with **Claude Code**.
>
> We chose it because our work was not one small script — it was many connected steps across the whole project: backend, frontend, tests, and the full deployment to Vercel. Claude Code is strong at these long, multi-file tasks, and it can read the build and error logs to fix problems by itself. For tiny edits, like a small style change, we used inline tools like Cursor.
>
> We **orchestrate** the agents with simple rules in two files in the repo: `AGENTS.md` and `CLAUDE.md`. They set the golden rules — for example, never fake the numbers, always keep the source tags, and never call the live AI inside tests. We also split the work like our team: one track for the data and AI backend, one track for the frontend and the investor story, with the README as the shared contract. Before a risky change, a second agent session reviews the difference against those rules.

---

## 9:05 – 9:45 · Scaling, operations, and security — **Zhen & Hidde**

> **Zhen:** To scale, the main change is the database. Today we use a simple file database with demo data. For real customers we move to a managed Postgres — that is a one-line change, no rewrite. The main technical risk is depending on one data feed, so we keep alternatives ready.
>
> **Hidde:** For operations, the AI can hit rate limits, so we added automatic retries and caching, and the app always falls back to rules. For security, the big points are: keep the API keys only on the server, never in the browser; use private model tiers in production so customer data is never used for training; and add proper login and access control before real client data goes in. In this demo, all data is synthetic on purpose.

---

## 9:45 – 10:00 · Close — **both**

> **Hidde:** So that is Green Cast: forward-looking risk intelligence, fully explainable, built for mid-market funds.
>
> **Zhen:** Rules for the math, AI for the words, and every number you can trace. Thank you for watching.

*[screen: landing page, then the GitHub repo link]*

---

### Speaker split summary

| Section | Speaker |
|---|---|
| Problem | Hidde |
| Solution & features | Zhen |
| Demo: portfolio, lineage, commentary | Hidde |
| Demo: interpretation, normalisation, screening, ROI | Zhen |
| Architecture & innovation→code & UX | Hidde |
| Deployment | Hidde |
| Investor case (market, revenue, competition) | Zhen |
| Coding agents & orchestration | Hidde |
| Scaling / operations / security | Zhen & Hidde |
| Close | Both |
