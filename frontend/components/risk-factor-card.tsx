"use client";

import { useState } from "react";
import { cn, factorLabel, riskBarColour, riskBadgeClass, riskLabel } from "@/lib/utils";
import type { RiskFactor, RiskFactorLineage } from "@/lib/types";

interface Props {
  factor: RiskFactor;
  isComposite?: boolean;
}

export function RiskFactorCard({ factor, isComposite = false }: Props) {
  const [open, setOpen] = useState(false);
  const [lineage, setLineage] = useState<RiskFactorLineage | null>(null);
  const [loading, setLoading] = useState(false);

  async function fetchLineage() {
    if (lineage) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/risk-factors/${factor.id}/lineage`,
      );
      setLineage(await res.json());
    } finally {
      setLoading(false);
    }
  }

  function toggle() {
    if (!open) fetchLineage();
    setOpen((p) => !p);
  }

  const score = factor.normalized_value;

  return (
    <div
      className={cn(
        "rounded-lg border bg-gc-surface shadow-sm transition",
        isComposite
          ? "border-gc-green/30 bg-gc-green/5"
          : "border-gc-border hover:border-gc-border/80",
      )}
    >
      {/* Header row — always visible */}
      <button
        onClick={toggle}
        className="flex w-full items-center gap-4 px-5 py-4 text-left"
        aria-expanded={open}
      >
        {/* Factor label */}
        <div className="min-w-0 flex-1">
          <p
            className={cn(
              "text-sm font-semibold",
              isComposite ? "text-gc-green" : "text-gc-text",
            )}
          >
            {factorLabel(factor.factor_type)}
            {isComposite && (
              <span className="ml-2 text-xs font-normal text-gc-muted">
                (weighted composite)
              </span>
            )}
          </p>
          <p className="mt-0.5 truncate text-xs text-gc-muted">
            {factor.raw_source_ref}
          </p>
        </div>

        {/* Score bar + value */}
        <div className="flex shrink-0 items-center gap-3">
          {!isComposite && (
            <div className="h-1.5 w-20 overflow-hidden rounded-full bg-gc-border">
              <div
                className={cn("h-full rounded-full", riskBarColour(score))}
                style={{ width: `${score}%` }}
              />
            </div>
          )}
          <span
            className={cn(
              "w-12 text-right font-mono text-sm font-semibold",
              isComposite ? "text-xl text-gc-green" : "text-gc-text",
            )}
          >
            {score.toFixed(1)}
          </span>
          {!isComposite && (
            <span
              className={cn(
                "w-16 rounded border px-2 py-0.5 text-center text-xs font-medium",
                riskBadgeClass(score),
              )}
            >
              {riskLabel(score)}
            </span>
          )}
          {!isComposite && (
            <span className="w-8 text-right text-xs text-gc-muted">
              {(factor.weight * 100).toFixed(0)}%
            </span>
          )}
        </div>

        {/* Expand chevron */}
        <span
          className={cn(
            "ml-1 text-gc-muted transition-transform",
            open && "rotate-180",
          )}
          aria-hidden
        >
          ▾
        </span>
      </button>

      {/* Lineage panel */}
      {open && (
        <div className="border-t border-gc-border/50 px-5 pb-5 pt-4">
          {loading && (
            <p className="text-xs text-gc-muted">Loading lineage…</p>
          )}

          {lineage && (
            <>
              {/* Transform description */}
              <div className="mb-4 rounded bg-gc-bg px-4 py-3 text-xs leading-relaxed text-gc-muted">
                <span className="font-medium text-gc-text">Transform: </span>
                {lineage.transform_description}
              </div>

              {/* Contributing inputs table */}
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-gc-muted">
                Contributing inputs
              </p>
              <div className="divide-y divide-gc-border/50 rounded border border-gc-border overflow-hidden">
                {lineage.risk_factor.contributing_inputs.map((inp, idx) => (
                  <div key={idx} className="grid grid-cols-[auto_1fr] gap-x-4 px-4 py-3 text-xs">
                    <div className="text-gc-muted">
                      <span className="font-medium text-gc-text">{inp.source_table}</span>
                      {inp.record_id && (
                        <span className="text-gc-muted"> #{inp.record_id}</span>
                      )}
                      <span className="block text-gc-muted/70">{inp.field}</span>
                      {inp.unit && (
                        <span className="text-gc-muted/60">{inp.unit}</span>
                      )}
                    </div>
                    <div>
                      {inp.raw_value !== null && inp.raw_value !== undefined && (
                        <span className="font-mono font-medium text-gc-text">
                          {typeof inp.raw_value === "number"
                            ? inp.raw_value.toLocaleString("en-EU", { maximumFractionDigits: 2 })
                            : inp.raw_value}
                          {"  "}
                        </span>
                      )}
                      <span className="text-gc-muted">{inp.description}</span>
                    </div>
                  </div>
                ))}
              </div>

              <p className="mt-3 text-right text-xs text-gc-muted">
                Weight in composite:{" "}
                <span className="font-mono font-medium text-gc-text">
                  {lineage.composite_weight_pct.toFixed(0)}%
                </span>
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
