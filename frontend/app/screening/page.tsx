"use client";

import { useState } from "react";
import { apiFetch, factorLabel } from "@/lib/utils";
import type { ScreeningVerdict } from "@/lib/types";

const CBAM_LEVELS = ["none", "low", "medium", "high"];

const RAG_STYLES: Record<string, string> = {
  green: "border-green-200 bg-green-50 text-green-800",
  amber: "border-amber-300 bg-amber-50 text-amber-800",
  red:   "border-gc-red/30 bg-red-50 text-gc-red",
};

const SEVERITY_COLOUR: Record<string, string> = {
  high:   "border-gc-red/30 bg-red-50 text-gc-red",
  medium: "border-amber-300 bg-amber-50 text-amber-800",
  low:    "border-gc-border bg-gc-bg text-gc-muted",
};

export default function ScreeningPage() {
  const [form, setForm] = useState({
    name: "",
    sector: "",
    country: "DE",
    carbon_intensity: 150,
    energy_dependency_score: 0.5,
    supplier_concentration: 0.4,
    epc_rating: "",
    revenue_em: 30,
    ebitda_em: 6,
    net_debt_em: 80,
    cbam_level: "none",
    ir_sensitivity: 0.5,
  });
  const [verdict, setVerdict] = useState<ScreeningVerdict | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function update(field: string, value: string | number) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  const isRE = form.epc_rating !== "";

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setVerdict(null);
    try {
      const payload = {
        ...form,
        epc_rating: form.epc_rating || null,
        carbon_intensity: Number(form.carbon_intensity),
        energy_dependency_score: Number(form.energy_dependency_score),
        supplier_concentration: Number(form.supplier_concentration),
        revenue_em: Number(form.revenue_em),
        ebitda_em: Number(form.ebitda_em),
        net_debt_em: Number(form.net_debt_em),
        ir_sensitivity: Number(form.ir_sensitivity),
      };
      const result = await apiFetch<ScreeningVerdict>("/screening/evaluate", {
        method: "POST",
        body: payload,
      });
      setVerdict(result);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-screen-xl px-6 py-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-gc-text">Pre-Investment Screening</h1>
        <p className="mt-1 text-sm text-gc-muted">
          Apply the same normalization engine and rules as portfolio monitoring to a prospective target —
          before acquisition.
        </p>
      </div>

      <div className="grid gap-10 lg:grid-cols-[1fr_480px]">
        {/* Input form */}
        <form onSubmit={submit} className="flex flex-col gap-6">
          {/* Identity */}
          <section className="rounded-lg border border-gc-border bg-gc-surface p-6 shadow-sm">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gc-muted">
              Target identity
            </h2>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Company name" required>
                <Input value={form.name} onChange={(v) => update("name", v)} placeholder="Acme GmbH" required />
              </Field>
              <Field label="Sector" required>
                <Input value={form.sector} onChange={(v) => update("sector", v)} placeholder="Chemicals" required />
              </Field>
              <Field label="Country">
                <Input value={form.country} onChange={(v) => update("country", v)} placeholder="DE" />
              </Field>
            </div>
          </section>

          {/* ESG inputs */}
          <section className="rounded-lg border border-gc-border bg-gc-surface p-6 shadow-sm">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gc-muted">
              ESG inputs
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Carbon intensity (tCO₂e/€M revenue)">
                <NumberInput value={form.carbon_intensity} onChange={(v) => update("carbon_intensity", v)} min={0} max={1000} />
              </Field>
              <Field label="Energy dependency (0–1)">
                <NumberInput value={form.energy_dependency_score} onChange={(v) => update("energy_dependency_score", v)} min={0} max={1} step={0.01} />
              </Field>
              <Field label="Supplier concentration (0–1)">
                <NumberInput value={form.supplier_concentration} onChange={(v) => update("supplier_concentration", v)} min={0} max={1} step={0.01} />
              </Field>
              <Field label="EPC rating (leave blank if not RE)">
                <select
                  value={form.epc_rating}
                  onChange={(e) => update("epc_rating", e.target.value)}
                  className="w-full rounded border border-gc-border bg-gc-bg px-3 py-2 text-sm text-gc-text focus:outline-none focus:ring-1 focus:ring-gc-green"
                >
                  <option value="">— not applicable (industrial) —</option>
                  {["A", "B", "C", "D", "E", "F", "G"].map((g) => (
                    <option key={g} value={g}>Grade {g}</option>
                  ))}
                </select>
              </Field>
              <Field label="CBAM exposure level">
                <select
                  value={form.cbam_level}
                  onChange={(e) => update("cbam_level", e.target.value)}
                  className="w-full rounded border border-gc-border bg-gc-bg px-3 py-2 text-sm text-gc-text focus:outline-none focus:ring-1 focus:ring-gc-green"
                >
                  {CBAM_LEVELS.map((l) => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </Field>
              {isRE && (
                <Field label="Interest rate sensitivity (0–1)">
                  <NumberInput value={form.ir_sensitivity} onChange={(v) => update("ir_sensitivity", v)} min={0} max={1} step={0.01} />
                </Field>
              )}
            </div>
          </section>

          {/* Financial inputs */}
          <section className="rounded-lg border border-gc-border bg-gc-surface p-6 shadow-sm">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gc-muted">
              Financial inputs (€M, single period)
            </h2>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Revenue (€M)">
                <NumberInput value={form.revenue_em} onChange={(v) => update("revenue_em", v)} min={0} />
              </Field>
              <Field label="EBITDA (€M)">
                <NumberInput value={form.ebitda_em} onChange={(v) => update("ebitda_em", v)} />
              </Field>
              <Field label="Net debt (€M)">
                <NumberInput value={form.net_debt_em} onChange={(v) => update("net_debt_em", v)} min={0} />
              </Field>
            </div>
          </section>

          <button
            type="submit"
            disabled={loading}
            className="self-start rounded bg-gc-green px-6 py-2.5 text-sm font-semibold text-white hover:bg-gc-green/90 disabled:opacity-50 transition"
          >
            {loading ? "Screening…" : "Run screening"}
          </button>

          {error && (
            <p className="text-sm text-gc-red">{error}</p>
          )}
        </form>

        {/* Verdict panel */}
        <div>
          {!verdict && !loading && (
            <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-gc-border text-sm text-gc-muted">
              Verdict will appear here
            </div>
          )}

          {verdict && (
            <div className="flex flex-col gap-4">
              {/* RAG header */}
              <div className={`rounded-lg border p-5 ${RAG_STYLES[verdict.rag_flag]}`}>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-semibold">{verdict.name}</p>
                    <p className="text-xs opacity-70">{verdict.sector}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-3xl font-bold">{verdict.overall_score.toFixed(1)}</p>
                    <p className="text-xs uppercase tracking-wider opacity-70">overall</p>
                  </div>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <p className="opacity-60 uppercase tracking-wider">Transition risk</p>
                    <p className="font-mono text-lg font-bold">{verdict.transition_score.toFixed(1)}</p>
                  </div>
                  <div>
                    <p className="opacity-60 uppercase tracking-wider">Financial risk</p>
                    <p className="font-mono text-lg font-bold">{verdict.financial_score.toFixed(1)}</p>
                  </div>
                </div>
              </div>

              {/* Top 3 factors */}
              {verdict.top_factors.length > 0 && (
                <div className="rounded-lg border border-gc-border bg-gc-surface p-4 shadow-sm">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gc-muted">
                    Top risk drivers
                  </p>
                  <div className="flex flex-col gap-2">
                    {verdict.top_factors.map((tf, i) => (
                      <div key={i} className="flex items-center justify-between text-sm">
                        <span className="text-gc-text">{factorLabel(tf.factor_type)}</span>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-20 overflow-hidden rounded-full bg-gc-border">
                            <div
                              className={`h-full rounded-full ${
                                tf.normalized_value < 34 ? "bg-gc-green" : tf.normalized_value < 67 ? "bg-amber-500" : "bg-gc-red"
                              }`}
                              style={{ width: `${tf.normalized_value}%` }}
                            />
                          </div>
                          <span className="w-10 text-right font-mono text-xs text-gc-text">
                            {tf.normalized_value.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Alerts */}
              {verdict.alerts.length > 0 && (
                <div className="rounded-lg border border-gc-border bg-gc-surface p-4 shadow-sm">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gc-muted">
                    Rules engine alerts ({verdict.alerts.length})
                  </p>
                  <div className="flex flex-col gap-2">
                    {verdict.alerts.map((alert, i) => (
                      <div
                        key={i}
                        className={`rounded border p-2.5 text-xs ${SEVERITY_COLOUR[alert.severity] ?? ""}`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold">{alert.category}</span>
                          <span className="font-mono text-[10px] opacity-70">{alert.rule_name}</span>
                        </div>
                        <p className="mt-1 opacity-80 leading-relaxed">{alert.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <p className="text-xs text-gc-muted">{verdict.engine_note}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Local form components ─────────────────────────────────────────────────────

function Field({ label, children, required }: { label: string; children: React.ReactNode; required?: boolean }) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs font-medium text-gc-muted">
        {label}{required && <span className="ml-0.5 text-gc-red">*</span>}
      </span>
      {children}
    </label>
  );
}

function Input({
  value, onChange, placeholder, required,
}: {
  value: string; onChange: (v: string) => void; placeholder?: string; required?: boolean;
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      required={required}
      className="rounded border border-gc-border bg-gc-bg px-3 py-2 text-sm text-gc-text placeholder-gc-border focus:outline-none focus:ring-1 focus:ring-gc-green"
    />
  );
}

function NumberInput({
  value, onChange, min, max, step,
}: {
  value: number; onChange: (v: number) => void; min?: number; max?: number; step?: number;
}) {
  return (
    <input
      type="number"
      value={value}
      onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
      min={min}
      max={max}
      step={step ?? 0.1}
      className="rounded border border-gc-border bg-gc-bg px-3 py-2 font-mono text-sm text-gc-text focus:outline-none focus:ring-1 focus:ring-gc-green"
    />
  );
}
