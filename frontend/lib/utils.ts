import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function riskColour(score: number): string {
  if (score < 34) return "text-gc-green";
  if (score < 67) return "text-amber-600";
  return "text-gc-red";
}

export function riskBarColour(score: number): string {
  if (score < 34) return "bg-gc-green";
  if (score < 67) return "bg-amber-500";
  return "bg-gc-red";
}

export function riskLabel(score: number): string {
  if (score < 34) return "Low";
  if (score < 67) return "Moderate";
  return "High";
}

export function riskBadgeClass(score: number): string {
  if (score < 34) return "bg-green-50 text-green-800 border border-green-200";
  if (score < 67) return "bg-amber-50 text-amber-800 border border-amber-200";
  return "bg-red-50 text-red-800 border border-red-200";
}

export function factorLabel(factorType: string): string {
  const labels: Record<string, string> = {
    OVERALL_RISK_SCORE: "Overall Risk Score",
    TRANSITION_RISK_COMPOSITE: "Transition Risk Composite",
    FINANCIAL_RISK_COMPOSITE: "Financial Risk Composite",
    CARBON_INTENSITY: "Carbon Intensity",
    ENERGY_DEPENDENCY: "Energy Dependency",
    SUPPLIER_CONCENTRATION: "Supplier Concentration",
    EPC_RATING: "EPC Rating",
    CBAM_EXPOSURE: "CBAM Exposure",
    INTEREST_RATE_SENSITIVITY: "Interest Rate Sensitivity",
    LTV_RATIO: "LTV (Real Estate)",
    LEVERAGE_RATIO: "Leverage (Net Debt / EBITDA)",
    EBITDA_MARGIN: "EBITDA Margin Risk",
  };
  return labels[factorType] ?? factorType;
}

export function strategyLabel(s: string): string {
  return { PE: "Private Equity", PC: "Private Credit", RE: "Real Estate" }[s] ?? s;
}

// Server components need an absolute URL; the browser uses the same-origin
// "/be" proxy (see next.config.mjs) to avoid CORS and the localhost fallback.
const SERVER_API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function apiBase(): string {
  return typeof window === "undefined" ? SERVER_API : "/be";
}

export async function apiFetch<T>(
  path: string,
  options?: { method?: string; body?: unknown }
): Promise<T> {
  const init: RequestInit = { next: { revalidate: 0 } };
  if (options?.method) init.method = options.method;
  if (options?.body !== undefined) {
    init.body = JSON.stringify(options.body);
    init.headers = { "Content-Type": "application/json" };
  }
  const res = await fetch(`${apiBase()}${path}`, init);
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}
