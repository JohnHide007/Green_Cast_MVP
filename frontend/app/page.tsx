import Link from "next/link";

const features = [
  {
    title: "Unified Risk Schema",
    body: "Financial, ESG, and macro signals normalised into a single RiskFactor model. Every score is traceable to the raw input that produced it.",
  },
  {
    title: "Hybrid AI + Rules Engine",
    body: "Deterministic rules compute the numbers. Claude writes the narrative on top — every sentence cites the rule and data point behind it.",
  },
  {
    title: "Pre-Investment Screening",
    body: "Run the same risk engine on prospective targets before acquisition. The same intelligence, applied pre-DD.",
  },
  {
    title: "In-Product ROI",
    body: "Quantify analyst hours saved versus subscription cost. Mid-market payback in under one quarter at default inputs.",
  },
];

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-screen-xl px-6">
      {/* Hero */}
      <section className="flex flex-col items-start gap-6 py-20 md:py-28">
        <p className="rounded border border-gc-green/30 bg-gc-green/5 px-3 py-1 text-xs font-medium uppercase tracking-wider text-gc-green">
          For European mid-market private equity, private credit &amp; real estate funds
        </p>

        <h1 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight text-gc-text md:text-5xl">
          Portfolio risk intelligence,{" "}
          <span className="text-gc-green">fully attributable</span>
        </h1>

        <p className="max-w-2xl text-lg text-gc-muted">
          Green Cast ingests portfolio company financials, ESG exposure metrics,
          and external regulatory signals — fusing them into forward-looking risk
          commentary for LP reports and investment committee memos. Every AI
          sentence traces back to the rule and data point that produced it.
        </p>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/funds"
            className="inline-flex items-center gap-2 rounded bg-gc-green px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-green-800"
          >
            View Demo Portfolio →
          </Link>
          <Link
            href="/screening"
            className="inline-flex items-center gap-2 rounded border border-gc-border bg-gc-surface px-5 py-2.5 text-sm font-semibold text-gc-text shadow-sm transition hover:bg-gc-border/30"
          >
            Pre-DD Screening
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-gc-border py-10">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {[
            ["30", "Portfolio companies"],
            ["3", "Funds across PE · PC · RE"],
            ["9", "Risk factor types"],
            ["100%", "Attributed AI output"],
          ].map(([val, label]) => (
            <div key={label}>
              <p className="font-mono text-3xl font-semibold text-gc-green">{val}</p>
              <p className="mt-1 text-sm text-gc-muted">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature grid */}
      <section className="py-16">
        <h2 className="mb-10 text-2xl font-bold tracking-tight">
          What the platform proves
        </h2>
        <div className="grid gap-6 md:grid-cols-2">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-lg border border-gc-border bg-gc-surface p-6 shadow-sm"
            >
              <h3 className="mb-2 font-semibold text-gc-text">{f.title}</h3>
              <p className="text-sm leading-relaxed text-gc-muted">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-gc-border py-8 text-xs text-gc-muted">
        Green Cast is a risk intelligence platform. Regulatory compliance is a
        byproduct, not the primary output.
      </footer>
    </div>
  );
}
