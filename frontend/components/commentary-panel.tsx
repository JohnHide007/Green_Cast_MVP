"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/utils";
import type { CommentaryResponse } from "@/lib/types";

interface Props {
  companyId: number;
}

export function CommentaryPanel({ companyId }: Props) {
  const [data, setData] = useState<CommentaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showSources, setShowSources] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const result = await apiFetch<CommentaryResponse>(
        `/portfolio/${companyId}/commentary`,
        { method: "POST" }
      );
      setData(result);
    } catch {
      setData({
        available: false,
        company_id: companyId,
        sentences: [],
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
          AI Risk Commentary
        </p>
        <p className="mb-4 text-xs text-gc-muted">
          Generate an attributed narrative drawn from computed risk factors and fired alerts.
        </p>
        <button
          onClick={load}
          className="rounded border border-gc-teal/40 bg-gc-surface px-4 py-1.5 text-xs font-medium text-gc-teal hover:bg-gc-teal/10 transition"
        >
          Generate commentary
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="rounded-lg border border-gc-teal/20 bg-gc-teal/5 p-5">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gc-teal">
          AI Risk Commentary
        </p>
        <div className="flex items-center gap-2 text-xs text-gc-muted">
          <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-gc-teal border-t-transparent" />
          Generating…
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gc-teal/20 bg-gc-teal/5 p-5">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-gc-teal">
          AI Risk Commentary
        </p>
        <div className="flex items-center gap-3">
          {data?.available && (
            <button
              onClick={() => setShowSources((s) => !s)}
              className="text-xs text-gc-muted underline-offset-2 hover:text-gc-teal hover:underline"
            >
              {showSources ? "Hide sources" : "Show sources"}
            </button>
          )}
          <button
            onClick={load}
            className="text-xs text-gc-muted hover:text-gc-teal"
            title="Regenerate"
          >
            ↺
          </button>
        </div>
      </div>

      {!data?.available ? (
        <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          {data?.message ?? "Commentary unavailable."}
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {data.sentences.map((s, i) => (
            <div key={i}>
              <p className="text-sm leading-relaxed text-gc-text">{s.sentence}</p>
              {showSources && s.source_refs.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {s.source_refs.map((ref) => (
                    <span
                      key={ref}
                      className="rounded bg-gc-teal/10 px-1.5 py-0.5 font-mono text-[10px] text-gc-teal"
                    >
                      {ref}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
