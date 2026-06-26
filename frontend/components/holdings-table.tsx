"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { riskBadgeClass, riskLabel } from "@/lib/utils";

const FLAG: Record<string, string> = {
  NL: "🇳🇱", DE: "🇩🇪", GB: "🇬🇧", BE: "🇧🇪", PL: "🇵🇱", EE: "🇪🇪",
};

export interface Holding {
  id: number;
  name: string;
  sector: string;
  country: string;
  entry_year: number;
  score: number | null;
}

type RatingFilter = "all" | "high" | "moderate" | "low";
type SortKey = "score" | "name" | "sector" | "entry";
type SortDir = "asc" | "desc";

function ratingOf(score: number | null): RatingFilter | null {
  if (score === null) return null;
  if (score >= 67) return "high";
  if (score >= 34) return "moderate";
  return "low";
}

function rowBorder(score: number | null): string {
  if (score === null) return "";
  if (score >= 67) return "border-l-[3px] border-l-gc-red";
  if (score >= 34) return "border-l-[3px] border-l-amber-400";
  return "border-l-[3px] border-l-gc-green";
}

export function HoldingsTable({ holdings }: { holdings: Holding[] }) {
  const [rating, setRating] = useState<RatingFilter>("all");
  const [sector, setSector] = useState<string>("all");
  const [sortKey, setSortKey] = useState<SortKey>("score");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const sectors = useMemo(
    () => Array.from(new Set(holdings.map((h) => h.sector))).sort(),
    [holdings],
  );

  const view = useMemo(() => {
    let rows = holdings.filter((h) => {
      if (rating !== "all" && ratingOf(h.score) !== rating) return false;
      if (sector !== "all" && h.sector !== sector) return false;
      return true;
    });
    rows = [...rows].sort((a, b) => {
      let cmp = 0;
      if (sortKey === "score") cmp = (a.score ?? -1) - (b.score ?? -1);
      else if (sortKey === "name") cmp = a.name.localeCompare(b.name);
      else if (sortKey === "sector") cmp = a.sector.localeCompare(b.sector);
      else if (sortKey === "entry") cmp = a.entry_year - b.entry_year;
      return sortDir === "asc" ? cmp : -cmp;
    });
    return rows;
  }, [holdings, rating, sector, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "name" || key === "sector" ? "asc" : "desc");
    }
  }

  const arrow = (key: SortKey) => (sortKey === key ? (sortDir === "asc" ? " ↑" : " ↓") : "");

  const RATINGS: { value: RatingFilter; label: string }[] = [
    { value: "all", label: "All" },
    { value: "high", label: "High" },
    { value: "moderate", label: "Moderate" },
    { value: "low", label: "Low" },
  ];

  return (
    <div>
      {/* Controls */}
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-1 rounded-lg border border-gc-border bg-gc-surface p-1">
          {RATINGS.map((r) => (
            <button
              key={r.value}
              onClick={() => setRating(r.value)}
              className={`rounded px-3 py-1 text-xs font-medium transition ${
                rating === r.value
                  ? "bg-gc-green/10 text-gc-green"
                  : "text-gc-muted hover:text-gc-text"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-gc-muted">Sector</label>
          <select
            value={sector}
            onChange={(e) => setSector(e.target.value)}
            className="rounded border border-gc-border bg-gc-surface px-2 py-1 text-xs text-gc-text focus:outline-none focus:ring-1 focus:ring-gc-green"
          >
            <option value="all">All sectors</option>
            {sectors.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <span className="ml-2 text-xs text-gc-muted">
            {view.length} of {holdings.length}
          </span>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-lg border border-gc-border bg-gc-surface shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gc-border bg-gc-bg text-left text-xs uppercase tracking-wider text-gc-muted">
              <SortTh onClick={() => toggleSort("name")} className="pl-5">Company{arrow("name")}</SortTh>
              <SortTh onClick={() => toggleSort("sector")}>Sector{arrow("sector")}</SortTh>
              <th className="px-4 py-3">Country</th>
              <SortTh onClick={() => toggleSort("entry")}>Entry{arrow("entry")}</SortTh>
              <SortTh onClick={() => toggleSort("score")} className="text-right">Risk Score{arrow("score")}</SortTh>
              <th className="px-4 py-3 text-right">Rating</th>
              <th className="w-10 px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gc-border">
            {view.map((h) => (
              <tr key={h.id} className={`transition hover:bg-gc-bg/60 ${rowBorder(h.score)}`}>
                <td className="px-4 py-3 pl-5 font-medium text-gc-text">
                  <Link href={`/portfolio/${h.id}`} className="hover:text-gc-green hover:underline">
                    {h.name}
                  </Link>
                </td>
                <td className="px-4 py-3 text-gc-muted">{h.sector}</td>
                <td className="px-4 py-3 text-gc-muted">{FLAG[h.country] ?? ""} {h.country}</td>
                <td className="px-4 py-3 font-mono text-gc-muted">{h.entry_year}</td>
                <td className="px-4 py-3 text-right">
                  {h.score !== null ? (
                    <div className="flex items-center justify-end gap-3">
                      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gc-border">
                        <div
                          className={`h-full rounded-full transition-all ${
                            h.score < 34 ? "gradient-bar-low" : h.score < 67 ? "gradient-bar-moderate" : "gradient-bar-high"
                          }`}
                          style={{ width: `${h.score}%` }}
                        />
                      </div>
                      <span className="w-12 text-right font-mono text-gc-text">{h.score.toFixed(1)}</span>
                    </div>
                  ) : (
                    <span className="text-gc-muted">—</span>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  {h.score !== null && (
                    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${riskBadgeClass(h.score)}`}>
                      {riskLabel(h.score)}
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  <Link href={`/portfolio/${h.id}`} className="text-xs text-gc-muted hover:text-gc-green">→</Link>
                </td>
              </tr>
            ))}
            {view.length === 0 && (
              <tr>
                <td colSpan={7} className="px-5 py-10 text-center text-sm text-gc-muted">
                  No holdings match these filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SortTh({
  children, onClick, className = "",
}: {
  children: React.ReactNode; onClick: () => void; className?: string;
}) {
  return (
    <th className={`px-4 py-3 ${className}`}>
      <button onClick={onClick} className="font-medium uppercase tracking-wider hover:text-gc-green transition-colors">
        {children}
      </button>
    </th>
  );
}
