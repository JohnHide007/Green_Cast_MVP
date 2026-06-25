"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/utils";
import type { NormalizationResponse } from "@/lib/types";

const SAMPLE = `[
  { "Boekjaar": 2023, "Kwartaal": 4, "Omzet": 12450000, "Bedrijfsresultaat": 2180000, "Nettoschuld": 5400000 },
  { "Boekjaar": 2023, "Kwartaal": 3, "Omzet": 11980000, "Bedrijfsresultaat": 2050000, "Nettoschuld": 5610000 }
]`;

export default function IngestionPage() {
  const [raw, setRaw] = useState(SAMPLE);
  const [hint, setHint] = useState("Exact (Dutch GL export)");
  const [data, setData] = useState<NormalizationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [parseError, setParseError] = useState<string | null>(null);

  async function run() {
    setParseError(null);
    let rows: unknown;
    try {
      rows = JSON.parse(raw);
      if (!Array.isArray(rows)) throw new Error("Expected a JSON array of rows.");
    } catch (e) {
      setParseError(e instanceof Error ? e.message : "Invalid JSON.");
      return;
    }
    setLoading(true);
    try {
      const result = await apiFetch<NormalizationResponse>("/ingestion/normalize", {
        method: "POST",
        body: { rows, source_hint: hint || null },
      });
      setData(result);
    } catch {
      setData({
        available: false,
        rows: [],
        field_mapping: {},
        notes: "",
        model: "",
        message: "Failed to reach backend.",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-screen-lg px-6 py-10">
      <h1 className="text-2xl font-bold text-gc-text">AI Data Normalisation</h1>
      <p className="mt-2 max-w-2xl text-sm text-gc-muted">
        Portfolio companies submit financials in inconsistent formats (Exact, SAP, Xero,
        Twinfield, Excel). Paste raw rows below — the AI maps arbitrary columns onto the
        canonical schema (year, quarter, revenue, EBITDA, net debt) with no bespoke connector.
      </p>

      <div className="mt-6 grid gap-4">
        <label className="text-xs font-semibold uppercase tracking-wider text-gc-muted">
          Source system (optional hint)
          <input
            value={hint}
            onChange={(e) => setHint(e.target.value)}
            className="mt-1 block w-full rounded border border-gc-border bg-gc-surface px-3 py-2 text-sm text-gc-text"
            placeholder="e.g. SAP, Xero, Excel export"
          />
        </label>

        <label className="text-xs font-semibold uppercase tracking-wider text-gc-muted">
          Raw rows (JSON array)
          <textarea
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            rows={10}
            className="mt-1 block w-full rounded border border-gc-border bg-gc-surface px-3 py-2 font-mono text-xs text-gc-text"
          />
        </label>

        {parseError && (
          <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-800">
            {parseError}
          </div>
        )}

        <div>
          <button
            onClick={run}
            disabled={loading}
            className="rounded bg-gc-teal px-5 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Normalising…" : "Normalise with AI"}
          </button>
        </div>
      </div>

      {data && (
        <div className="mt-8">
          {!data.available ? (
            <div className="rounded border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              {data.message ?? "Normalisation unavailable."}
            </div>
          ) : (
            <div className="grid gap-6">
              <div>
                <h2 className="mb-2 text-sm font-semibold text-gc-text">Inferred field mapping</h2>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(data.field_mapping).map(([src, dst]) => (
                    <span key={src} className="rounded border border-gc-border bg-gc-surface px-2 py-1 font-mono text-xs text-gc-text">
                      {src} <span className="text-gc-muted">→</span> <span className="text-gc-teal">{dst}</span>
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h2 className="mb-2 text-sm font-semibold text-gc-text">Normalised rows</h2>
                <div className="overflow-x-auto rounded border border-gc-border">
                  <table className="w-full text-sm">
                    <thead className="bg-gc-border/30 text-left text-xs uppercase text-gc-muted">
                      <tr>
                        <th className="px-3 py-2">Year</th>
                        <th className="px-3 py-2">Quarter</th>
                        <th className="px-3 py-2">Revenue</th>
                        <th className="px-3 py-2">EBITDA</th>
                        <th className="px-3 py-2">Net debt</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.rows.map((r, i) => (
                        <tr key={i} className="border-t border-gc-border">
                          <td className="px-3 py-2">{r.year ?? "—"}</td>
                          <td className="px-3 py-2">{r.quarter ?? "—"}</td>
                          <td className="px-3 py-2 font-mono">{r.revenue?.toLocaleString() ?? "—"}</td>
                          <td className="px-3 py-2 font-mono">{r.ebitda?.toLocaleString() ?? "—"}</td>
                          <td className="px-3 py-2 font-mono">{r.net_debt?.toLocaleString() ?? "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {data.notes && <p className="text-xs text-gc-muted">{data.notes}</p>}
              {data.model && <p className="text-[10px] text-gc-muted">via Vercel AI Gateway · {data.model}</p>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
