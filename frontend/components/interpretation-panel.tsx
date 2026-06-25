"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/utils";
import type { RiskInterpretationResponse } from "@/lib/types";

interface Props {
  companyId: number;
}

const sevClass: Record<string, string> = {
  high: "bg-red-50 text-red-800 border border-red-200",
  medium: "bg-amber-50 text-amber-800 border border-amber-200",
  low: "bg-green-50 text-green-800 border border-green-200",
};

export function InterpretationPanel({ companyId }: Props) {
  const [data, setData] = useState<RiskInterpretationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const result = await apiFetch<RiskInterpretationResponse>(
        `/portfolio/${companyId}/interpretation`,
        { method: "POST" }
      );
      setData(result);
    } catch {
      setData({
        available: false,
        company_id: companyId,
        thesis: "",
        key_risks: [],
        model: "",
        message: "Failed to reach backend.",
      });
    } finally {
      setLoading(false);
    }
  }

  if (!data && !loading) {
    return (
      <div className="rounded-lg border border-gc-teal/20 bg-gc-teal/5 p-5">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gc-teal">
          AI Risk Interpretation
        </p>
        <p className="mb-4 text-xs text-gc-muted">
          Synthesise internal factors, alerts, and external macro/regulatory signals
          into a forward-looking risk thesis.
        </p>
        <button
          onClick={load}
          className="rounded border border-gc-teal/40 bg-gc-surface px-4 py-1.5 text-xs font-medium text-gc-teal hover:bg-gc-teal/10 transition"
        >
          Generate interpretation
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="rounded-lg border border-gc-teal/20 bg-gc-teal/5 p-5">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gc-teal">
          AI Risk Interpretation
        </p>
        <div className="flex items-center gap-2 text-xs text-gc-muted">
          <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-gc-teal border-t-transparent" />
          Synthesising…
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gc-teal/20 bg-gc-teal/5 p-5">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-gc-teal">
          AI Risk Interpretation
        </p>
        <button onClick={load} className="text-xs text-gc-muted hover:text-gc-teal" title="Regenerate">
          ↺
        </button>
      </div>

      {!data?.available ? (
        <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          {data?.message ?? "Interpretation unavailable."}
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          <p className="text-sm leading-relaxed text-gc-text">{data.thesis}</p>
          <div className="flex flex-col gap-2">
            {data.key_risks.map((r, i) => (
              <div key={i} className="rounded border border-gc-border bg-gc-surface p-3">
                <div className="mb-1 flex items-center justify-between gap-2">
                  <span className="text-sm font-semibold text-gc-text">{r.title}</span>
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${sevClass[r.severity] ?? ""}`}>
                    {r.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-gc-muted">{r.rationale}</p>
                {r.source_refs.length > 0 && (
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    {r.source_refs.map((ref) => (
                      <span key={ref} className="rounded bg-gc-teal/10 px-1.5 py-0.5 font-mono text-[10px] text-gc-teal">
                        {ref}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
          {data.model && (
            <p className="text-[10px] text-gc-muted">via Vercel AI Gateway · {data.model}</p>
          )}
        </div>
      )}
    </div>
  );
}
