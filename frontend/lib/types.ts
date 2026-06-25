export type FundStrategy = "PE" | "PC" | "RE";

export interface Fund {
  id: number;
  name: string;
  country: string;
  strategy: FundStrategy;
  currency: string;
}

export interface PortfolioCompany {
  id: number;
  fund_id: number;
  name: string;
  sector: string;
  country: string;
  entry_year: number;
}

export interface FundPortfolio {
  fund: Fund;
  companies: PortfolioCompany[];
}

export interface FinancialRecord {
  id: number;
  company_id: number;
  year: number;
  quarter: number;
  revenue: number;
  ebitda: number;
  net_debt: number;
}

export interface ESGMetric {
  id: number;
  company_id: number;
  carbon_intensity: number;
  energy_dependency_score: number;
  supplier_concentration: number;
  epc_rating: string | null;
}

export interface ContributingInput {
  source_table: string;
  record_id: number | null;
  field: string;
  raw_value: number | string | null;
  unit: string | null;
  description: string;
}

export interface RiskFactor {
  id: number;
  company_id: number;
  factor_type: string;
  raw_source_ref: string;
  normalized_value: number;
  weight: number;
  contributing_inputs: ContributingInput[];
  last_updated: string;
}

export interface RiskFactorLineage {
  risk_factor: RiskFactor;
  transform_description: string;
  composite_weight_pct: number;
}

export interface RiskAlert {
  id: number;
  company_id: number;
  rule_name: string;
  severity: "low" | "medium" | "high";
  category: string;
  description: string;
  threshold_value: number | null;
  actual_value: number | null;
  created_at: string;
}

export interface PortfolioCompanyDetail {
  id: number;
  fund_id: number;
  name: string;
  sector: string;
  country: string;
  entry_year: number;
  financials: FinancialRecord[];
  esg_metrics: ESGMetric[];
}

// ── Commentary ────────────────────────────────────────────────────────────────

export interface CommentarySentence {
  sentence: string;
  source_refs: string[];
}

export interface CommentaryResponse {
  available: boolean;
  company_id: number;
  sentences: CommentarySentence[];
  message?: string;
}

// ── Screening ─────────────────────────────────────────────────────────────────

export interface ScreeningTopFactor {
  factor_type: string;
  normalized_value: number;
  weight: number;
}

export interface ScreeningAlert {
  rule_name: string;
  severity: "low" | "medium" | "high";
  category: string;
  description: string;
  threshold_value: number | null;
  actual_value: number | null;
}

export interface ScreeningVerdict {
  name: string;
  sector: string;
  overall_score: number;
  transition_score: number;
  financial_score: number;
  rag_flag: "red" | "amber" | "green";
  top_factors: ScreeningTopFactor[];
  alerts: ScreeningAlert[];
  engine_note: string;
}

// ── ROI ───────────────────────────────────────────────────────────────────────

export interface RoiInput {
  portfolio_companies: number;
  hours_per_company_per_report: number;
  reports_per_year: number;
  analyst_rate_eur: number;
  tier: string;
}

export interface RoiResult {
  annual_hours_saved: number;
  annual_eur_saved: number;
  greencast_annual_cost: number;
  net_saving: number;
  payback_months: number;
  payback_display: string;
  tier: string;
  tier_label: string;
  inputs: RoiInput;
}
