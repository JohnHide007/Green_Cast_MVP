import Link from "next/link";
import { RoiCalculator } from "@/components/roi-calculator";

// ── Inline SVG feature icons ─────────────────────────────────────────────────

function IconSchema() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <rect x="2" y="4" width="24" height="5" rx="1.5" stroke="#2E7D32" strokeWidth="1.5" />
      <rect x="2" y="12" width="24" height="5" rx="1.5" stroke="#2E7D32" strokeWidth="1.5" />
      <rect x="2" y="20" width="24" height="5" rx="1.5" stroke="#2E7D32" strokeWidth="1.5" />
      <circle cx="6.5" cy="6.5" r="1" fill="#2E7D32" />
      <circle cx="6.5" cy="14.5" r="1" fill="#2E7D32" />
      <circle cx="6.5" cy="22.5" r="1" fill="#2E7D32" />
    </svg>
  );
}

function IconBrain() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <path d="M10 6C10 6 7 7 7 11C7 13 8 14.5 8 14.5C8 14.5 6 15.5 6 18C6 20.5 8 22 10 22H18C20 22 22 20.5 22 18C22 15.5 20 14.5 20 14.5C20 14.5 21 13 21 11C21 7 18 6 18 6" stroke="#2E7D32" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M10 6C10 4.5 12 4 14 4C16 4 18 4.5 18 6" stroke="#2E7D32" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M14 4V22" stroke="#2E7D32" strokeWidth="1.2" strokeLinecap="round" strokeDasharray="2 2" />
      <path d="M8 14.5H20" stroke="#2E7D32" strokeWidth="1.2" strokeLinecap="round" />
      <circle cx="10" cy="18" r="1.2" fill="#2E7D32" />
      <circle cx="18" cy="18" r="1.2" fill="#2E7D32" />
    </svg>
  );
}

function IconSearch() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="7" stroke="#2E7D32" strokeWidth="1.5" />
      <path d="M17.5 17.5L24 24" stroke="#2E7D32" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M9 12H15" stroke="#2E7D32" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M12 9V15" stroke="#2E7D32" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

function IconROI() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
      <rect x="3" y="3" width="10" height="10" rx="1.5" stroke="#2E7D32" strokeWidth="1.5" />
      <rect x="15" y="3" width="10" height="10" rx="1.5" stroke="#2E7D32" strokeWidth="1.5" />
      <rect x="3" y="15" width="10" height="10" rx="1.5" stroke="#2E7D32" strokeWidth="1.5" />
      <path d="M19 21L21 19L23 21" stroke="#2E7D32" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M15.5 21.5L19 19" stroke="#2E7D32" strokeWidth="1.3" strokeLinecap="round" />
      <path d="M6 8H10" stroke="#2E7D32" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M18 8H22" stroke="#2E7D32" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M6 20H10" stroke="#2E7D32" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

// ── Dashboard SVG mockup (right side of hero) ────────────────────────────────

function DashboardMockup() {
  // Three risk-score rings with labels
  const rings = [
    { cx: 60, score: 72, colour: "#B91C1C", label: "Nordex GmbH", tier: "HIGH" },
    { cx: 160, score: 41, colour: "#D97706", label: "AquaPort RE", tier: "MOD" },
    { cx: 260, score: 18, colour: "#2E7D32", label: "LogisCo NL", tier: "LOW" },
  ];

  function ring(cx: number, score: number, colour: string, label: string, tier: string) {
    const r = 30;
    const circ = 2 * Math.PI * r;
    const dash = (score / 100) * circ * 0.75; // 270° arc → *0.75
    return (
      <g key={cx}>
        {/* Track */}
        <circle cx={cx} cy={60} r={r} fill="none" stroke="#1e3a22" strokeWidth="6" />
        {/* Fill */}
        <circle
          cx={cx}
          cy={60}
          r={r}
          fill="none"
          stroke={colour}
          strokeWidth="6"
          strokeDasharray={`${dash} ${circ}`}
          strokeDashoffset={circ * 0.125}
          strokeLinecap="round"
          transform={`rotate(-225 ${cx} 60)`}
        />
        {/* Score text */}
        <text x={cx} y={64} textAnchor="middle" fontSize="13" fontWeight="700" fill={colour} fontFamily="monospace">
          {score}
        </text>
        {/* Tier badge */}
        <rect x={cx - 14} y={98} width="28" height="12" rx="3" fill={colour} fillOpacity="0.18" />
        <text x={cx} y={108} textAnchor="middle" fontSize="7" fontWeight="600" fill={colour} fontFamily="monospace" letterSpacing="0.04em">
          {tier}
        </text>
        {/* Company label */}
        <text x={cx} y={122} textAnchor="middle" fontSize="7.5" fill="#8fbf8f" fontFamily="Inter, sans-serif">
          {label}
        </text>
      </g>
    );
  }

  return (
    <div className="relative w-full max-w-sm lg:max-w-md">
      {/* Floating card */}
      <div className="rounded-xl border border-[#1e3a22] bg-[#0d1f10]/90 p-5 shadow-2xl backdrop-blur">
        {/* Card header */}
        <div className="mb-4 flex items-center justify-between">
          <span className="font-mono text-xs font-semibold uppercase tracking-wider text-[#4ade80]">
            Live Risk Monitor
          </span>
          <span className="flex items-center gap-1.5 text-xs text-[#4ade80]/60">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#4ade80] animate-pulse" />
            3 holdings
          </span>
        </div>

        {/* SVG rings */}
        <svg viewBox="0 0 320 135" className="w-full">
          {rings.map((r) => ring(r.cx, r.score, r.colour, r.label, r.tier))}
        </svg>

        {/* Mini table */}
        <div className="mt-4 divide-y divide-[#1e3a22]">
          {[
            { name: "Carbon Intensity", val: "68.2", colour: "#B91C1C" },
            { name: "Leverage Ratio",   val: "41.5", colour: "#D97706" },
            { name: "EPC Rating",       val: "18.0", colour: "#2E7D32" },
          ].map((row) => (
            <div key={row.name} className="flex items-center justify-between py-1.5">
              <span className="font-mono text-xs text-[#8fbf8f]">{row.name}</span>
              <span className="font-mono text-xs font-bold" style={{ color: row.colour }}>
                {row.val}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Decorative glow */}
      <div
        className="pointer-events-none absolute -inset-4 rounded-2xl opacity-20"
        style={{ background: "radial-gradient(ellipse at center, #2E7D32 0%, transparent 70%)" }}
      />
    </div>
  );
}

// ── Feature data ─────────────────────────────────────────────────────────────

const features = [
  {
    Icon: IconSchema,
    title: "Unified Risk Schema",
    body: "Financial, ESG, and macro signals normalised into a single RiskFactor model. Every score is traceable to the raw input that produced it.",
  },
  {
    Icon: IconBrain,
    title: "Hybrid AI + Rules Engine",
    body: "Deterministic rules compute the numbers. An LLM writes the narrative on top (via Vercel AI Gateway) — every sentence cites the rule and data point behind it.",
  },
  {
    Icon: IconSearch,
    title: "Pre-Investment Screening",
    body: "Run the same risk engine on prospective targets before acquisition. The same intelligence, applied pre-DD.",
  },
  {
    Icon: IconROI,
    title: "In-Product ROI",
    body: "Quantify analyst hours saved versus subscription cost. Mid-market payback in under one quarter at default inputs.",
  },
];

// ── Page ─────────────────────────────────────────────────────────────────────

export default function LandingPage() {
  return (
    <div>
      {/* ── Dark hero ── */}
      <section
        className="relative w-full overflow-hidden"
        style={{
          background: "linear-gradient(135deg, #0a1a0d 0%, #0f2d14 50%, #091810 100%)",
        }}
      >
        {/* Dot grid overlay */}
        <div className="hero-dot-grid absolute inset-0 pointer-events-none" />

        {/* Content */}
        <div className="relative mx-auto flex max-w-screen-xl flex-col items-start gap-0 px-6 py-20 md:flex-row md:items-center md:gap-12 md:py-28">
          {/* Left copy */}
          <div className="flex-1 flex flex-col gap-6 animate-fade-up">
            {/* Eyebrow */}
            <p className="inline-flex w-fit items-center gap-2 rounded-full border border-[#2E7D32]/40 bg-[#2E7D32]/10 px-3 py-1 text-xs font-medium uppercase tracking-wider text-[#4ade80]">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#4ade80]" />
              For European mid-market PE · PC · RE funds
            </p>

            <h1 className="max-w-xl text-4xl font-bold leading-tight tracking-tight text-white md:text-5xl lg:text-6xl">
              Portfolio risk intelligence,{" "}
              <span className="text-[#4ade80]">fully attributable</span>
            </h1>

            <p className="max-w-lg text-lg leading-relaxed" style={{ color: "rgba(255,255,255,0.65)" }}>
              Green Cast ingests portfolio company financials, ESG exposure metrics,
              and external regulatory signals — fusing them into forward-looking risk
              commentary for LP reports and investment committee memos. Every AI
              sentence traces back to the rule and data point that produced it.
            </p>

            <div className="flex flex-wrap gap-3">
              <Link
                href="/funds"
                className="inline-flex items-center gap-2 rounded-md bg-white px-5 py-2.5 text-sm font-semibold text-[#0a1a0d] shadow-sm transition hover:bg-gray-100"
              >
                View Demo Portfolio →
              </Link>
              <Link
                href="/screening"
                className="inline-flex items-center gap-2 rounded-md border border-white/30 px-5 py-2.5 text-sm font-semibold text-white transition hover:border-white/60 hover:bg-white/5"
              >
                Pre-DD Screening
              </Link>
            </div>
          </div>

          {/* Right: dashboard mockup */}
          <div className="mt-10 flex justify-center md:mt-0 md:justify-end animate-fade-up delay-300">
            <DashboardMockup />
          </div>
        </div>
      </section>

      {/* ── Impact stats (card layout) ── */}
      <section className="border-b border-gc-border bg-gc-bg py-16 md:py-20">
        <div className="mx-auto max-w-screen-xl px-6">
          <h2 className="mb-10 text-2xl font-bold tracking-tight text-gc-text md:text-3xl">
            The impact
          </h2>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { value: "60–80 hrs", body: "Analyst time per fund every quarter, today spent consolidating spreadsheets by hand.", k: "Basis", v: "Per fund / quarter" },
              { value: "Weeks → hours", body: "Reporting cycle once the engine drafts the commentary.", k: "Scope", v: "Per reporting cycle" },
              { value: "~80%", body: "Of the report write-up step automated, at default ROI inputs.", k: "Step", v: "Commentary write-up" },
              { value: "63%", body: "Of firms already using or planning AI for ESG data.", k: "Signal", v: "Industry adoption*" },
            ].map((s) => (
              <div
                key={s.value}
                className="flex flex-col rounded-2xl border border-gc-border bg-gc-surface p-7 shadow-sm transition hover:shadow-md"
              >
                <p className="text-4xl font-bold tracking-tight text-gc-green">{s.value}</p>
                <p className="mt-3 flex-1 text-sm leading-relaxed text-gc-muted">{s.body}</p>
                <div className="mt-6 flex items-center justify-between border-t border-gc-border pt-4">
                  <span className="text-xs font-semibold uppercase tracking-wider text-gc-muted">{s.k}</span>
                  <span className="text-xs font-medium text-gc-text">{s.v}</span>
                </div>
              </div>
            ))}
          </div>
          <p className="mt-8 max-w-3xl text-xs leading-relaxed text-gc-muted">
            *Industry adoption benchmark. Private credit AUM alone stands at ~$1.6T and is projected to triple by 2029,
            with mid-market funds under sustained CSRD / SFDR reporting pressure.
          </p>
        </div>
      </section>

      {/* ── Feature grid ── */}
      <section className="bg-gc-bg py-20">
        <div className="mx-auto max-w-screen-xl px-6">
          <div className="mb-12">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gc-green">
              Platform capabilities
            </p>
            <h2 className="text-2xl font-bold tracking-tight text-gc-text md:text-3xl">
              What the platform proves
            </h2>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {features.map((f) => (
              <div
                key={f.title}
                className="group rounded-2xl border border-gc-border bg-gc-surface p-7 shadow-sm transition hover:border-gc-green/40 hover:shadow-md"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-gc-green/10 transition group-hover:bg-gc-green/20">
                  <f.Icon />
                </div>
                <h3 className="mb-2 font-semibold text-gc-text">{f.title}</h3>
                <p className="text-sm leading-relaxed text-gc-muted">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Why funds use it ── */}
      <section className="border-t border-gc-border bg-gc-surface py-20">
        <div className="mx-auto max-w-screen-xl px-6">
          <div className="mb-12">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gc-green">
              Why funds use Green Cast
            </p>
            <h2 className="max-w-2xl text-2xl font-bold tracking-tight text-gc-text md:text-3xl">
              Forward-looking risk intelligence, not another compliance snapshot
            </h2>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {[
              ["Catch risk early", "Flags operational and regulatory risk before it shows up in the financials — the opposite of a backward-looking quarterly report."],
              ["One unified view", "Financials, ESG exposure and macro signals normalise into a single score. Click any number to see the raw input and the transform behind it."],
              ["Investor-ready output", "Commentary drops straight into LP reports and IC memos without analyst rewriting — and every sentence is attributable to a rule or data point."],
              ["Built for the mid-market", "Modular, days-not-weeks onboarding and pricing sized for sub-€2bn funds that enterprise tools like MSCI or Sustainalytics price out."],
            ].map(([title, body]) => (
              <div key={title} className="rounded-2xl border border-gc-border bg-gc-surface p-7 shadow-sm">
                <div className="mb-3 h-1.5 w-8 rounded-full bg-gc-green" />
                <h3 className="mb-2 font-semibold text-gc-text">{title}</h3>
                <p className="text-sm leading-relaxed text-gc-muted">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ROI calculator ── */}
      <section className="bg-gc-bg py-20" id="roi">
        <div className="mx-auto max-w-screen-xl px-6">
          <div className="mb-10 max-w-2xl">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gc-green">
              See the payback
            </p>
            <h2 className="text-2xl font-bold tracking-tight text-gc-text md:text-3xl">
              What it saves your fund
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-gc-muted">
              Estimate the analyst hours Green Cast replaces versus the subscription cost.
              Most mid-market funds reach payback in under a quarter on default inputs.
            </p>
          </div>
          <RoiCalculator />
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="border-t border-gc-border bg-gc-surface py-20" id="faq">
        <div className="mx-auto max-w-screen-xl px-6">
          <div className="mb-10">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gc-green">
              FAQ
            </p>
            <h2 className="text-2xl font-bold tracking-tight text-gc-text md:text-3xl">
              Common questions
            </h2>
          </div>
          <div className="mx-auto max-w-3xl divide-y divide-gc-border rounded-2xl border border-gc-border bg-gc-bg">
            {[
              ["How long does it take to get my portfolio up and running?", "Days, not weeks. Your portfolio companies send financials in whatever format they already use — Exact, SAP, Xero, Twinfield, Excel — and the AI normalisation engine maps them onto one schema. There's no bespoke connector to build for each source."],
              ["Can I actually trust the AI commentary in an LP report?", "Yes — it's designed to be audited, not taken on faith. Deterministic rules compute every number; the AI only writes the narrative on top, and each sentence cites the exact rule or data point behind it. You can hand it to an investment committee and trace any claim to its source."],
              ["How is this different from MSCI ESG or Sustainalytics?", "Those are enterprise tools with per-portfolio onboarding cycles that only pay off at multi-billion-euro scale. Green Cast is purpose-built for sub-€2bn mid-market funds, and it fuses financial, ESG and macro signals into one forward-looking risk layer instead of isolated compliance snapshots."],
              ["Will it keep me ahead of CSRD and SFDR?", "It maps signals for CSRD, SFDR, EU Taxonomy, CBAM and AIFMD II to specific holdings, surfacing regulatory exposure before it becomes a reporting scramble. As the rules compound, one unified intelligence layer only gets more valuable."],
              ["Do I still need my analysts?", "It removes the grunt work, not the judgement. Analysts stop burning 60–80 hours a quarter consolidating spreadsheets and rewriting commentary, and spend that time on the investment decisions the report exists to support."],
              ["Is my portfolio data kept private?", "Your data is never used to train any model. Commentary runs through the Vercel AI Gateway on a private/paid model tier in production, and this demo runs entirely on synthetic holdings."],
              ["What does it cost?", "Recurring SaaS, tiered by portfolio size — Starter, Growth and Enterprise — with onboarding and API/white-label reporting as add-ons. Use the calculator above to see the payback for your own fund."],
            ].map(([q, a]) => (
              <details key={q} className="group px-6 py-4">
                <summary className="flex cursor-pointer items-center justify-between text-sm font-medium text-gc-text marker:content-['']">
                  {q}
                  <span className="ml-4 text-gc-muted transition-transform group-open:rotate-45">+</span>
                </summary>
                <p className="mt-3 text-sm leading-relaxed text-gc-muted">{a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-gc-border bg-gc-surface py-8">
        <div className="mx-auto max-w-screen-xl px-6 text-xs text-gc-muted">
          Green Cast is a risk intelligence platform. Regulatory compliance is a
          byproduct, not the primary output.
        </div>
      </footer>
    </div>
  );
}
