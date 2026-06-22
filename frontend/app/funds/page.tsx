import Link from "next/link";
import { apiFetch, strategyLabel } from "@/lib/utils";

export const dynamic = "force-dynamic";
import type { Fund } from "@/lib/types";

const FLAG: Record<string, string> = {
  NL: "🇳🇱", DE: "🇩🇪", GB: "🇬🇧", BE: "🇧🇪", PL: "🇵🇱", EE: "🇪🇪",
};

const STRATEGY_COLOUR: Record<string, string> = {
  PE: "bg-purple-50 text-purple-800 border-purple-200",
  PC: "bg-blue-50  text-blue-800  border-blue-200",
  RE: "bg-amber-50 text-amber-800 border-amber-200",
};

export default async function FundsPage() {
  const funds = await apiFetch<Fund[]>("/funds");

  return (
    <div className="mx-auto max-w-screen-xl px-6 py-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-gc-text">Portfolio Monitoring</h1>
        <p className="mt-1 text-sm text-gc-muted">
          {funds.length} funds — {" "}
          <span className="text-gc-text">select a fund to view holdings and risk exposure</span>
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {funds.map((fund) => (
          <Link
            key={fund.id}
            href={`/funds/${fund.id}`}
            className="group rounded-lg border border-gc-border bg-gc-surface p-6 shadow-sm transition hover:border-gc-green/40 hover:shadow-md"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h2 className="font-semibold text-gc-text group-hover:text-gc-green">
                  {fund.name}
                </h2>
                <p className="mt-1 text-xs text-gc-muted">
                  {FLAG[fund.country] ?? ""} {fund.country} &middot; {fund.currency}
                </p>
              </div>
              <span
                className={`rounded border px-2 py-0.5 text-xs font-medium ${STRATEGY_COLOUR[fund.strategy] ?? ""}`}
              >
                {strategyLabel(fund.strategy)}
              </span>
            </div>
            <p className="mt-4 text-sm text-gc-muted group-hover:text-gc-green">
              View holdings →
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
