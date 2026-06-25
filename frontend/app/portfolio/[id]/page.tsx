import Link from "next/link";
import { apiFetch, riskLabel, riskBadgeClass, factorLabel } from "@/lib/utils";

export const dynamic = "force-dynamic";
import { RiskFactorCard } from "@/components/risk-factor-card";
import { CommentaryPanel } from "@/components/commentary-panel";
import { RiskGauge } from "@/components/risk-gauge";
import type {
  PortfolioCompanyDetail,
  RiskFactor,
  RiskAlert,
  FundPortfolio,
} from "@/lib/types";

const FLAG: Record<string, string> = {
  NL: "🇳🇱", DE: "🇩🇪", GB: "🇬🇧", BE: "🇧🇪", PL: "🇵🇱", EE: "🇪🇪",
};

const SEVERITY_COLOUR: Record<string, string> = {
  high:   "border-gc-red/30   bg-red-50   text-gc-red",
  medium: "border-amber-300   bg-amber-50 text-amber-800",
  low:    "border-gc-border   bg-gc-bg    text-gc-muted",
};

const COMPOSITE_TYPES = new Set([
  "OVERALL_RISK_SCORE",
  "TRANSITION_RISK_COMPOSITE",
  "FINANCIAL_RISK_COMPOSITE",
]);

export default async function CompanyRiskPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [company, factors, alerts] = await Promise.all([
    apiFetch<PortfolioCompanyDetail>(`/portfolio/${id}`),
    apiFetch<RiskFactor[]>(`/portfolio/${id}/risk-factors`),
    apiFetch<RiskAlert[]>(`/portfolio/${id}/risk-alerts`),
  ]);

  let fundName = "";
  try {
    const fp = await apiFetch<FundPortfolio>(`/funds/${company.fund_id}/portfolio`);
    fundName = fp.fund.name;
  } catch {}

  const overall = factors.find((f) => f.factor_type === "OVERALL_RISK_SCORE");
  const composites = factors.filter(
    (f) => COMPOSITE_TYPES.has(f.factor_type) && f.factor_type !== "OVERALL_RISK_SCORE"
  );
  const components = factors.filter((f) => !COMPOSITE_TYPES.has(f.factor_type));
  const latestFin = company.financials.at(-1);
  const esg = company.esg_metrics[0];

  return (
    <div>
      {/* ── Hero banner ── */}
      <div
        className="w-full"
        style={{
          background: "linear-gradient(135deg, #0a1a0d 0%, #0f2d14 60%, #091810 100%)",
        }}
      >
        <div className="mx-auto max-w-screen-xl px-6 py-6">
          {/* Breadcrumb */}
          <div className="mb-4 flex items-center gap-2 text-xs" style={{ color: "rgba(255,255,255,0.5)" }}>
            <Link href="/funds" className="hover:text-white transition-colors">Funds</Link>
            <span>›</span>
            {fundName && (
              <>
                <Link href={`/funds/${company.fund_id}`} className="hover:text-white transition-colors">
                  {fundName}
                </Link>
                <span>›</span>
              </>
            )}
            <span style={{ color: "rgba(255,255,255,0.8)" }}>{company.name}</span>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">{company.name}</h1>
              <p className="mt-1 text-sm" style={{ color: "rgba(255,255,255,0.55)" }}>
                {company.sector} · {FLAG[company.country] ?? ""} {company.country} · Entry {company.entry_year}
              </p>
            </div>

            {/* Overall gauge */}
            {overall && (
              <div className="flex items-center gap-5">
                <RiskGauge score={overall.normalized_value} size="lg" />
                <span
                  className={`rounded-full border px-4 py-1.5 text-sm font-semibold ${riskBadgeClass(overall.normalized_value)}`}
                >
                  {riskLabel(overall.normalized_value)}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Body ── */}
      <div className="mx-auto max-w-screen-xl px-6 py-10">
        <div className="grid gap-10 lg:grid-cols-[1fr_340px]">
          {/* Left: risk factors */}
          <div className="flex flex-col gap-8">
            {/* Sub-composites with mini gauges */}
            {composites.length > 0 && (
              <div className="grid gap-4 sm:grid-cols-2">
                {composites.map((c) => (
                  <div
                    key={c.id}
                    className="rounded-lg border border-gc-border bg-gc-surface p-5 shadow-sm"
                  >
                    <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gc-muted">
                      {factorLabel(c.factor_type)}
                    </p>
                    <div className="flex items-center gap-4">
                      <RiskGauge score={c.normalized_value} size="sm" />
                      <div>
                        <p className="font-mono text-xl font-bold text-gc-text">
                          {c.normalized_value.toFixed(1)}
                          <span className="ml-1 text-xs font-normal text-gc-muted">/100</span>
                        </p>
                        <p className="mt-1 text-xs text-gc-muted">
                          {Math.round(c.weight * 100)}% of overall
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Component factors */}
            <div>
              <div className="mb-3 flex items-center gap-2">
                <h2 className="text-base font-semibold text-gc-text">Risk Factor Breakdown</h2>
                <span className="text-xs text-gc-muted">— click any factor to reveal data lineage</span>
              </div>
              <div className="flex flex-col gap-3">
                {overall && <RiskFactorCard factor={overall} isComposite />}
                {components.map((f) => (
                  <RiskFactorCard key={f.id} factor={f} />
                ))}
              </div>
            </div>

            {/* AI commentary */}
            <CommentaryPanel companyId={company.id} />

            {/* Schema unity note */}
            <div className="rounded border border-gc-teal/20 bg-gc-teal/5 px-4 py-3 text-xs text-gc-muted">
              <span className="font-medium text-gc-teal">Data lineage: </span>
              All scores share one canonical{" "}
              <code className="rounded bg-gc-bg px-1 py-0.5 font-mono text-gc-text">RiskFactor</code>{" "}
              schema — financial records, ESG metrics, and macro signals all normalise into the same
              0–100 scale. Click any factor to see the exact raw values, source table, and transform
              formula.
            </div>
          </div>

          {/* Sidebar: raw data + alerts */}
          <aside className="flex flex-col gap-5">
            {latestFin && (
              <div className="rounded-lg border border-gc-border bg-gc-surface shadow-sm overflow-hidden">
                <div className="border-b border-gc-border bg-gc-bg px-5 py-3">
                  <p className="text-xs font-semibold uppercase tracking-wider text-gc-muted">
                    Financials · Q{latestFin.quarter} {latestFin.year}
                  </p>
                </div>
                <div className="divide-y divide-gc-border/50 px-5">
                  {[
                    ["Revenue",      `€${latestFin.revenue.toFixed(1)}M`],
                    ["EBITDA",       `€${latestFin.ebitda.toFixed(1)}M`],
                    ["EBITDA Margin",`${((latestFin.ebitda / latestFin.revenue) * 100).toFixed(1)}%`],
                    ["Net Debt",     `€${latestFin.net_debt.toFixed(0)}M`],
                  ].map(([label, val]) => (
                    <div key={label} className="flex justify-between py-2.5 text-sm">
                      <span className="text-gc-muted">{label}</span>
                      <span className="font-mono font-medium text-gc-text">{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {esg && (
              <div className="rounded-lg border border-gc-border bg-gc-surface shadow-sm overflow-hidden">
                <div className="border-b border-gc-border bg-gc-bg px-5 py-3">
                  <p className="text-xs font-semibold uppercase tracking-wider text-gc-muted">
                    ESG Metrics (raw)
                  </p>
                </div>
                <div className="divide-y divide-gc-border/50 px-5">
                  {[
                    ["Carbon Intensity",      `${esg.carbon_intensity} tCO₂e/€M`],
                    ["Energy Dependency",     `${(esg.energy_dependency_score * 100).toFixed(0)}%`],
                    ["Supplier Concentration",`${(esg.supplier_concentration * 100).toFixed(0)}%`],
                    ...(esg.epc_rating ? [["EPC Rating", `Grade ${esg.epc_rating}`] as [string, string]] : []),
                  ].map(([label, val]) => (
                    <div key={label} className="flex justify-between py-2.5 text-sm">
                      <span className="text-gc-muted">{label}</span>
                      <span className="font-mono font-medium text-gc-text">{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {alerts.length > 0 && (
              <div className="rounded-lg border border-gc-border bg-gc-surface shadow-sm overflow-hidden">
                <div className="border-b border-gc-border bg-gc-bg px-5 py-3">
                  <p className="text-xs font-semibold uppercase tracking-wider text-gc-muted">
                    Risk Alerts ({alerts.length})
                  </p>
                </div>
                <div className="flex flex-col gap-2 p-4">
                  {alerts.map((alert) => (
                    <div
                      key={alert.id}
                      className={`rounded border p-3 text-xs ${SEVERITY_COLOUR[alert.severity] ?? ""}`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold">{alert.category}</span>
                        <span className="font-mono text-xs opacity-70">{alert.rule_name}</span>
                      </div>
                      <p className="mt-1 leading-relaxed opacity-80">{alert.description}</p>
                      {alert.threshold_value !== null && alert.actual_value !== null && (
                        <p className="mt-1 font-mono opacity-60">
                          threshold: {alert.threshold_value} · actual: {alert.actual_value}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}
