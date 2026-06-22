import Link from "next/link";
import { apiFetch, riskBadgeClass, riskLabel, strategyLabel } from "@/lib/utils";

export const dynamic = "force-dynamic";
import type { FundPortfolio, RiskFactor } from "@/lib/types";

const FLAG: Record<string, string> = {
  NL: "🇳🇱", DE: "🇩🇪", GB: "🇬🇧", BE: "🇧🇪", PL: "🇵🇱", EE: "🇪🇪",
};

async function getCompositeScore(companyId: number): Promise<number | null> {
  try {
    const factors = await apiFetch<RiskFactor[]>(`/portfolio/${companyId}/risk-factors`);
    const overall = factors.find((f) => f.factor_type === "OVERALL_RISK_SCORE");
    return overall?.normalized_value ?? null;
  } catch {
    return null;
  }
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

  return (
    <div className="mx-auto max-w-screen-xl px-6 py-12">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <Link href="/funds" className="mb-2 inline-block text-xs text-gc-muted hover:text-gc-green">
            ← Funds
          </Link>
          <h1 className="text-2xl font-bold tracking-tight text-gc-text">{fund.name}</h1>
          <p className="mt-1 text-sm text-gc-muted">
            {strategyLabel(fund.strategy)} · {FLAG[fund.country] ?? ""} {fund.country} · {fund.currency} ·{" "}
            {companies.length} holdings
          </p>
        </div>
      </div>

      {/* Holdings table */}
      <div className="overflow-hidden rounded-lg border border-gc-border bg-gc-surface shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gc-border bg-gc-bg text-left text-xs uppercase tracking-wider text-gc-muted">
              <th className="px-4 py-3">Company</th>
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
                  className="transition hover:bg-gc-bg/60"
                >
                  <td className="px-4 py-3 font-medium text-gc-text">
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
                        <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gc-border">
                          <div
                            className={`h-full rounded-full transition-all ${
                              score < 34
                                ? "bg-gc-green"
                                : score < 67
                                ? "bg-amber-500"
                                : "bg-gc-red"
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
                        className={`rounded border px-2 py-0.5 text-xs font-medium ${riskBadgeClass(score)}`}
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
