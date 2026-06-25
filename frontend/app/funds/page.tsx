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

// Strategy-specific tint for the card header gradient
const STRATEGY_HEADER: Record<string, string> = {
  PE: "from-[#1a1030] to-[#0a1a0d]",
  PC: "from-[#081a22] to-[#0a1a0d]",
  RE: "from-[#1f1400] to-[#0a1a0d]",
};

// Inline SVG illustrations per strategy
function IllustrationPE() {
  return (
    <svg width="72" height="52" viewBox="0 0 72 52" fill="none" aria-hidden="true">
      {/* Upward bar chart */}
      <rect x="4"  y="36" width="10" height="12" rx="1.5" fill="#2E7D32" fillOpacity="0.5" />
      <rect x="18" y="26" width="10" height="22" rx="1.5" fill="#2E7D32" fillOpacity="0.65" />
      <rect x="32" y="16" width="10" height="32" rx="1.5" fill="#2E7D32" fillOpacity="0.8" />
      <rect x="46" y="8"  width="10" height="40" rx="1.5" fill="#2E7D32" />
      {/* Trend arrow */}
      <path d="M8 34L22 24L36 14L50 6" stroke="#4ade80" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M44 6H50V12" stroke="#4ade80" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IllustrationPC() {
  return (
    <svg width="72" height="52" viewBox="0 0 72 52" fill="none" aria-hidden="true">
      {/* Factory / industrial building */}
      <rect x="4"  y="24" width="20" height="24" rx="1.5" fill="#2E7D32" fillOpacity="0.5" />
      <rect x="28" y="16" width="16" height="32" rx="1.5" fill="#2E7D32" fillOpacity="0.7" />
      <rect x="48" y="28" width="16" height="20" rx="1.5" fill="#2E7D32" fillOpacity="0.55" />
      {/* Chimney stacks */}
      <rect x="8"  y="14" width="4" height="10" rx="1" fill="#4ade80" fillOpacity="0.5" />
      <rect x="14" y="18" width="4" height="6"  rx="1" fill="#4ade80" fillOpacity="0.5" />
      <rect x="32" y="8"  width="4" height="8"  rx="1" fill="#4ade80" fillOpacity="0.5" />
      {/* Ground line */}
      <line x1="2" y1="48" x2="66" y2="48" stroke="#2E7D32" strokeWidth="1" strokeOpacity="0.4" />
    </svg>
  );
}

function IllustrationRE() {
  return (
    <svg width="72" height="52" viewBox="0 0 72 52" fill="none" aria-hidden="true">
      {/* City buildings skyline */}
      <rect x="2"  y="28" width="14" height="20" rx="1.5" fill="#2E7D32" fillOpacity="0.45" />
      <rect x="18" y="18" width="16" height="30" rx="1.5" fill="#2E7D32" fillOpacity="0.65" />
      <rect x="36" y="10" width="18" height="38" rx="1.5" fill="#2E7D32" fillOpacity="0.85" />
      <rect x="56" y="22" width="12" height="26" rx="1.5" fill="#2E7D32" fillOpacity="0.55" />
      {/* Windows */}
      <rect x="21" y="22" width="4" height="4" rx="0.5" fill="#4ade80" fillOpacity="0.5" />
      <rect x="27" y="22" width="4" height="4" rx="0.5" fill="#4ade80" fillOpacity="0.5" />
      <rect x="39" y="14" width="4" height="4" rx="0.5" fill="#4ade80" fillOpacity="0.7" />
      <rect x="46" y="14" width="4" height="4" rx="0.5" fill="#4ade80" fillOpacity="0.7" />
      <rect x="39" y="22" width="4" height="4" rx="0.5" fill="#4ade80" fillOpacity="0.5" />
      {/* Ground line */}
      <line x1="2" y1="48" x2="68" y2="48" stroke="#2E7D32" strokeWidth="1" strokeOpacity="0.4" />
    </svg>
  );
}

const ILLUSTRATIONS: Record<string, React.FC> = {
  PE: IllustrationPE,
  PC: IllustrationPC,
  RE: IllustrationRE,
};

export default async function FundsPage() {
  const funds = await apiFetch<Fund[]>("/funds");

  return (
    <div className="mx-auto max-w-screen-xl px-6 py-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-gc-text">Portfolio Monitoring</h1>
        <p className="mt-1 text-sm text-gc-muted">
          {funds.length} funds —{" "}
          <span className="text-gc-text">select a fund to view holdings and risk exposure</span>
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {funds.map((fund) => {
          const Illustration = ILLUSTRATIONS[fund.strategy] ?? IllustrationPE;
          const headerGradient = STRATEGY_HEADER[fund.strategy] ?? "from-[#0a1a0d] to-[#091810]";

          return (
            <Link
              key={fund.id}
              href={`/funds/${fund.id}`}
              className="group rounded-lg border border-gc-border bg-gc-surface shadow-sm transition hover:border-gc-green/50 hover:shadow-lg hover:-translate-y-0.5"
            >
              {/* Illustrated header */}
              <div
                className={`relative flex items-end justify-between overflow-hidden rounded-t-lg bg-gradient-to-br ${headerGradient} px-5 pt-4 pb-3`}
              >
                {/* Strategy badge */}
                <span
                  className={`relative z-10 rounded border px-2 py-0.5 text-xs font-semibold ${STRATEGY_COLOUR[fund.strategy] ?? ""}`}
                >
                  {strategyLabel(fund.strategy)}
                </span>
                {/* Illustration */}
                <div className="relative z-10 opacity-90 group-hover:opacity-100 transition-opacity">
                  <Illustration />
                </div>
                {/* Subtle dot grid on header */}
                <div
                  className="absolute inset-0 opacity-30"
                  style={{
                    backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)",
                    backgroundSize: "18px 18px",
                  }}
                />
              </div>

              {/* Card body */}
              <div className="p-5">
                <h2 className="font-semibold text-gc-text group-hover:text-gc-green transition-colors">
                  {fund.name}
                </h2>
                <p className="mt-1 text-xs text-gc-muted">
                  {FLAG[fund.country] ?? ""} {fund.country} &middot; {fund.currency}
                </p>
                <p className="mt-4 text-sm font-medium text-gc-muted group-hover:text-gc-green transition-colors">
                  View holdings →
                </p>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
