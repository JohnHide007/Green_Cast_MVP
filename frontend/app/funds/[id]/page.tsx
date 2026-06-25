import Link from "next/link";
import { apiFetch, riskBadgeClass, riskLabel, strategyLabel } from "@/lib/utils";

export const dynamic = "force-dynamic";
import type { FundPortfolio, RiskFactor } from "@/lib/types";

const FLAG: Record<string, string> = {
  NL: "🇳🇱", DE: "🇩🇪", GB: "🇬🇧", BE: "🇧🇪", PL: "🇵🇱", EE: "🇪🇪",
};

// Strategy icons (small inline SVG)
function StrategyIcon({ strategy }: { strategy: string }) {
  if (strategy === "RE") {
    return (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true" className="shrink-0">
        <rect x="1" y="8"  width="5"  height="9"  rx="1" fill="currentColor" fillOpacity="0.5" />
        <rect x="7" y="5"  width="5"  height="12" rx="1" fill="currentColor" fillOpacity="0.75" />
        <rect x="13" y="10" width="4" height="7"  rx="1" fill="currentColor" fillOpacity="0.5" />
      </svg>
    );
  }
  if (strategy === "PC") {
    return (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true" className="shrink-0">
        <rect x="1" y="7"  width="6"  height="10" rx="1" fill="currentColor" fillOpacity="0.5" />
        <rect x="9" y="4"  width="5"  height="13" rx="1" fill="currentColor" fillOpacity="0.75" />
        <rect x="2" y="4"  width="2"  height="3"  rx="0.5" fill="currentColor" fillOpacity="0.4" />
      </svg>
    );
  }
  // PE — upward chart
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true" className="shrink-0">
      <rect x="1"  y="10" width="3" height="7" rx="0.8" fill="currentColor" fillOpacity="0.45" />
      <rect x="5"  y="7"  width="3" height="10" rx="0.8" fill="currentColor" fillOpacity="0.6" />
      <rect x="9"  y="4"  width="3" height="13" rx="0.8" fill="currentColor" fillOpacity="0.75" />
      <rect x="13" y="1"  width="3" height="16" rx="0.8" fill="currentColor" />
    </svg>
  );
}

async function getCompositeScore(companyId: number): Promise<number | null> {
  try {
    const factors = await apiFetch<RiskFactor[]>(`/portfolio/${companyId}/risk-factors`);
    const overall = factors.find((f) => f.factor_type === "OVERALL_RISK_SCORE");
    return overall?.normalized_value ?? null;
  } catch {
    return null;
  }
}

function riskRowBorder(score: number | null): string {
  if (score === null) return "";
  if (score >= 67) return "border-l-[3px] border-l-gc-red";
  if (score >= 34) return "border-l-[3px] border-l-amber-400";
  return "border-l-[3px] border-l-gc-green";
}

export default async function FundDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const { fund, companies } = await apiFetch<FundPortfolio>(`/funds/${id}/portfolio`);

  const scores = await Promise.all(
    companies.map((c) => getCompositeScore(c.id)),
  );

  // Risk summary counts
  const high     = scores.filter((s) => s !== null && s >= 67).length;
  const moderate = scores.filter((s) => s !== null && s >= 34 && s < 67).length;
  const low      = scores.filter((s) => s !== null && s < 34).length;

  return (
    <div className="mx-auto max-w-screen-xl px-6 py-12">
      {/* Header */}
      <div className="mb-8">
        <Link href="/funds" className="mb-3 inline-flex items-center gap-1 text-xs text-gc-muted hover:text-gc-green transition-colors">
          ← Funds
        </Link>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gc-green/10 text-gc-green">
              <StrategyIcon strategy={fund.strategy} />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-gc-text">{fund.name}</h1>
              <p className="mt-0.5 text-sm text-gc-muted">
                {strategyLabel(fund.strategy)} · {FLAG[fund.country] ?? ""} {fund.country} · {fund.currency} ·{" "}
                {companies.length} holdings
              </p>
            </div>
          </div>

          {/* Risk summary pills */}
          <div className="flex items-center gap-2 text-xs font-medium">
            {high > 0 && (
              <span className="rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-gc-red">
                {high} high
              </span>
            )}
            {moderate > 0 && (
              <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-amber-800">
                {moderate} moderate
              </span>
            )}
            {low > 0 && (
              <span className="rounded-full border border-green-200 bg-green-50 px-2.5 py-1 text-green-800">
                {low} low
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Holdings table */}
      <div className="overflow-hidden rounded-lg border border-gc-border bg-gc-surface shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gc-border bg-gc-bg text-left text-xs uppercase tracking-wider text-gc-muted">
              <th className="px-4 py-3 pl-5">Company</th>
              <th className="px-4 py-3">Sector</th>
              <th className="px-4 py-3">Country</th>
              <th className="px-4 py-3">Entry</th>
              <th className="px-4 py-3 text-right">Risk Score</th>
              <th className="px-4 py-3 text-right">Rating</th>
              <th className="w-10 px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gc-border">
            {companies.map((company, i) => {
              const score = scores[i];
              return (
                <tr
                  key={company.id}
                  className={`transition hover:bg-gc-bg/60 ${riskRowBorder(score)}`}
                >
                  <td className="px-4 py-3 pl-5 font-medium text-gc-text">
                    <Link
                      href={`/portfolio/${company.id}`}
                      className="hover:text-gc-green hover:underline"
                    >
                      {company.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-gc-muted">{company.sector}</td>
                  <td className="px-4 py-3 text-gc-muted">
                    {FLAG[company.country] ?? ""} {company.country}
                  </td>
                  <td className="px-4 py-3 font-mono text-gc-muted">{company.entry_year}</td>
                  <td className="px-4 py-3 text-right">
                    {score !== null ? (
                      <div className="flex items-center justify-end gap-3">
                        {/* Gradient progress bar */}
                        <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gc-border">
                          <div
                            className={`h-full rounded-full transition-all ${
                              score < 34
                                ? "gradient-bar-low"
                                : score < 67
                                ? "gradient-bar-moderate"
                                : "gradient-bar-high"
                            }`}
                            style={{ width: `${score}%` }}
                          />
                        </div>
                        <span className="w-12 text-right font-mono text-gc-text">
                          {score.toFixed(1)}
                        </span>
                      </div>
                    ) : (
                      <span className="text-gc-muted">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {score !== null && (
                      <span
                        className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${riskBadgeClass(score)}`}
                      >
                        {riskLabel(score)}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/portfolio/${company.id}`}
                      className="text-xs text-gc-muted hover:text-gc-green"
                    >
                      →
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
