"use client";

import { useState } from "react";
import { cn, factorLabel, riskBadgeClass, riskLabel } from "@/lib/utils";
import type { RiskFactor, RiskFactorLineage } from "@/lib/types";

interface Props {
  factor: RiskFactor;
  isComposite?: boolean;
}

function gradientBarClass(score: number): string {
  if (score < 34) return "gradient-bar-low";
  if (score < 67) return "gradient-bar-moderate";
  return "gradient-bar-high";
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
          : score >= 67
            ? "border-gc-border border-l-[3px] border-l-gc-red hover:border-l-gc-red"
            : score >= 34
              ? "border-gc-border border-l-[3px] border-l-amber-400 hover:border-l-amber-400"
              : "border-gc-border border-l-[3px] border-l-gc-green hover:border-l-gc-green",
        !isComposite && score >= 67 && "animate-pulse-risk",
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
                className={cn("h-full rounded-full", gradientBarClass(score))}
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
                "w-16 rounded-full border px-2 py-0.5 text-center text-xs font-medium",
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
            "ml-1 text-gc-muted transition-transform duration-200",
            open && "rotate-180",
          )}
          aria-hidden
        >
          ▾
        </span>
      </button>

      {/* Terminal lineage drawer */}
      {open && (
        <div className="terminal-drawer px-5 pb-5 pt-4">
          {loading && (
            <p className="terminal-comment py-2">// loading lineage…</p>
          )}

          {lineage && (
            <>
              {/* Transform as a code comment */}
              <div className="mb-4 terminal-comment">
                {"/* "}Transform: {lineage.transform_description}{" */"}
              </div>

              {/* Contributing inputs */}
              <div className="terminal-table-header mb-2">
                Contributing inputs
              </div>

              <div className="rounded overflow-hidden border border-[#1e2a1e]">
                {lineage.risk_factor.contributing_inputs.map((inp, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      "grid grid-cols-[180px_1fr] gap-x-4 px-4 py-2.5",
                      idx % 2 === 1 ? "terminal-row-alt" : "",
                    )}
                  >
                    {/* Left: source info */}
                    <div className="flex flex-col gap-0.5">
                      <span className="terminal-field">{inp.source_table}</span>
                      {inp.record_id && (
                        <span className="terminal-comment">#{inp.record_id}</span>
                      )}
                      <span style={{ color: "#6dbf6d", opacity: 0.8 }}>{inp.field}</span>
                      {inp.unit && (
                        <span className="terminal-comment">{inp.unit}</span>
                      )}
                    </div>

                    {/* Right: value + description */}
                    <div className="flex flex-col justify-center gap-0.5">
                      {inp.raw_value !== null && inp.raw_value !== undefined && (
                        <span className="terminal-value">
                          {typeof inp.raw_value === "number"
                            ? inp.raw_value.toLocaleString("en-EU", { maximumFractionDigits: 2 })
                            : inp.raw_value}
                        </span>
                      )}
                      <span className="terminal-comment">{inp.description}</span>
                    </div>
                  </div>
                ))}
              </div>

              <p className="mt-3 text-right terminal-comment">
                {"// "}weight in composite:{" "}
                <span className="terminal-value font-semibold">
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
