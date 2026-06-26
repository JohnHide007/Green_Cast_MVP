"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/utils";
import type { RoiResult } from "@/lib/types";

const TIERS = [
  { value: "starter",    label: "Starter",    price: "€12,000 / yr", note: "Up to 10 holdings" },
  { value: "growth",     label: "Growth",     price: "€24,000 / yr", note: "Up to 50 holdings" },
  { value: "enterprise", label: "Enterprise", price: "€48,000 / yr", note: "Unlimited"           },
];

export function RoiCalculator() {
  const [form, setForm] = useState({
    portfolio_companies: 25,
    hours_per_company_per_report: 12,
    reports_per_year: 4,
    analyst_rate_eur: 120,
    tier: "growth",
  });
  const [result, setResult] = useState<RoiResult | null>(null);
  const [loading, setLoading] = useState(false);

  function update(field: string, value: number | string) {
    setForm((f) => ({ ...f, [field]: value }));
    setResult(null);
  }

  async function calculate() {
    setLoading(true);
    try {
      const r = await apiFetch<RoiResult>("/roi/calculate", { method: "POST", body: form });
      setResult(r);
    } finally {
      setLoading(false);
    }
  }

  const fmtEur = (n: number) =>
    new Intl.NumberFormat("en-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);

  return (
    <div className="grid gap-10 lg:grid-cols-[420px_1fr]">
      {/* Inputs */}
      <div className="flex flex-col gap-6">
        <section className="rounded-lg border border-gc-border bg-gc-surface p-6 shadow-sm">
          <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gc-muted">
            Your portfolio
          </h3>
          <div className="flex flex-col gap-4">
            <RoiField label="Portfolio companies" unit="companies">
              <RoiNumber value={form.portfolio_companies} min={1} max={500}
                onChange={(v) => update("portfolio_companies", v)} />
            </RoiField>
            <RoiField label="Analyst hours per company per report" unit="hrs">
              <RoiNumber value={form.hours_per_company_per_report} min={1} max={200} step={1}
                onChange={(v) => update("hours_per_company_per_report", v)} />
            </RoiField>
            <RoiField label="Reports per year" unit="×/yr">
              <RoiNumber value={form.reports_per_year} min={1} max={52} step={1}
                onChange={(v) => update("reports_per_year", v)} />
            </RoiField>
            <RoiField label="Analyst loaded rate" unit="€/hr">
              <RoiNumber value={form.analyst_rate_eur} min={50} max={500} step={10}
                onChange={(v) => update("analyst_rate_eur", v)} />
            </RoiField>
          </div>
        </section>

        <section className="rounded-lg border border-gc-border bg-gc-surface p-6 shadow-sm">
          <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gc-muted">
            Green Cast tier
          </h3>
          <div className="flex flex-col gap-2">
            {TIERS.map((t) => (
              <button
                key={t.value}
                type="button"
                onClick={() => update("tier", t.value)}
                className={`flex items-center justify-between rounded border px-4 py-3 text-sm transition ${
                  form.tier === t.value
                    ? "border-gc-green bg-gc-green/5 text-gc-green"
                    : "border-gc-border bg-gc-bg text-gc-text hover:border-gc-green/40"
                }`}
              >
                <div className="text-left">
                  <span className="font-semibold">{t.label}</span>
                  <span className="ml-2 text-xs opacity-60">{t.note}</span>
                </div>
                <span className="font-mono text-xs">{t.price}</span>
              </button>
            ))}
          </div>
        </section>

        <button
          onClick={calculate}
          disabled={loading}
          className="rounded bg-gc-green px-6 py-2.5 text-sm font-semibold text-white hover:bg-gc-green/90 disabled:opacity-50 transition"
        >
          {loading ? "Calculating…" : "Calculate ROI"}
        </button>
      </div>

      {/* Results */}
      <div>
        {!result && !loading && (
          <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-gc-border text-sm text-gc-muted">
            Enter your numbers and calculate to see payback and net savings
          </div>
        )}

        {result && (
          <div className="flex flex-col gap-4">
            <div className="rounded-lg border border-gc-green/30 bg-gc-green/5 p-6">
              <p className="text-xs font-semibold uppercase tracking-wider text-gc-muted">
                Payback period
              </p>
              <p className="font-mono text-5xl font-bold text-gc-green">{result.payback_display}</p>
              <p className="mt-1 text-sm text-gc-muted">{result.tier_label}</p>
            </div>

            <div className="rounded-lg border border-gc-border bg-gc-surface shadow-sm overflow-hidden">
              <table className="w-full text-sm">
                <tbody className="divide-y divide-gc-border">
                  {[
                    ["Annual hours saved",     `${result.annual_hours_saved.toLocaleString()} hrs`, ""],
                    ["Annual value saved",     fmtEur(result.annual_eur_saved),                     ""],
                    ["Green Cast annual cost",  fmtEur(result.greencast_annual_cost),               "text-gc-muted"],
                    ["Net annual saving",      fmtEur(result.net_saving),                           "font-semibold text-gc-green"],
                  ].map(([label, val, cls]) => (
                    <tr key={label}>
                      <td className="px-5 py-3 text-gc-muted">{label}</td>
                      <td className={`px-5 py-3 text-right font-mono ${cls}`}>{val}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="rounded border border-gc-teal/20 bg-gc-teal/5 px-4 py-3 text-xs text-gc-muted">
              <span className="font-medium text-gc-teal">Assumptions: </span>
              {result.inputs.portfolio_companies} companies ×{" "}
              {result.inputs.hours_per_company_per_report} hrs ×{" "}
              {result.inputs.reports_per_year} reports/year × 80% automation saving ={" "}
              {result.annual_hours_saved} hrs saved · loaded rate €{result.inputs.analyst_rate_eur}/hr
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function RoiField({ label, unit, children }: { label: string; unit: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <label className="text-sm text-gc-text">
        {label} <span className="text-xs text-gc-muted">({unit})</span>
      </label>
      <div className="w-28 shrink-0">{children}</div>
    </div>
  );
}

function RoiNumber({
  value, onChange, min, max, step,
}: {
  value: number; onChange: (v: number) => void; min?: number; max?: number; step?: number;
}) {
  return (
    <input
      type="number"
      value={value}
      min={min}
      max={max}
      step={step ?? 1}
      onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
      className="w-full rounded border border-gc-border bg-gc-bg px-3 py-1.5 text-right font-mono text-sm text-gc-text focus:outline-none focus:ring-1 focus:ring-gc-green"
    />
  );
}
