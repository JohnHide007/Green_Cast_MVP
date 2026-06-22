import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from sqlmodel import Field, Relationship, SQLModel


class FundStrategy(str, Enum):
    PE = "PE"
    PC = "PC"
    RE = "RE"


class RiskSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class FactorType(str, Enum):
    # ── Climate / regulatory component factors ────────────────────────────────
    CARBON_INTENSITY        = "CARBON_INTENSITY"
    ENERGY_DEPENDENCY       = "ENERGY_DEPENDENCY"
    SUPPLIER_CONCENTRATION  = "SUPPLIER_CONCENTRATION"
    EPC_RATING              = "EPC_RATING"           # RE only
    CBAM_EXPOSURE           = "CBAM_EXPOSURE"
    # ── Financial / leverage component factors ────────────────────────────────
    INTEREST_RATE_SENSITIVITY = "INTEREST_RATE_SENSITIVITY"  # RE only
    LTV_RATIO               = "LTV_RATIO"            # RE: net_debt/revenue
    LEVERAGE_RATIO          = "LEVERAGE_RATIO"        # Industrial: net_debt/EBITDA
    EBITDA_MARGIN           = "EBITDA_MARGIN"
    # ── Composites ───────────────────────────────────────────────────────────
    TRANSITION_RISK_COMPOSITE = "TRANSITION_RISK_COMPOSITE"   # climate/regulatory only
    FINANCIAL_RISK_COMPOSITE  = "FINANCIAL_RISK_COMPOSITE"    # leverage/financial only
    OVERALL_RISK_SCORE        = "OVERALL_RISK_SCORE"           # TR + FR weighted


# ── Fund ─────────────────────────────────────────────────────────────────────

class Fund(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    country: str
    strategy: FundStrategy
    currency: str = "EUR"

    companies: list["PortfolioCompany"] = Relationship(back_populates="fund")


# ── PortfolioCompany ──────────────────────────────────────────────────────────

class PortfolioCompany(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fund_id: int = Field(foreign_key="fund.id")
    name: str
    sector: str
    country: str
    entry_year: int

    fund: Optional[Fund] = Relationship(back_populates="companies")
    financials: list["FinancialRecord"] = Relationship(back_populates="company")
    esg_metrics: list["ESGMetric"] = Relationship(back_populates="company")
    macro_signals: list["MacroSignal"] = Relationship(back_populates="company")
    risk_factors: list["RiskFactor"] = Relationship(back_populates="company")
    risk_alerts: list["RiskAlert"] = Relationship(back_populates="company")


# ── FinancialRecord ───────────────────────────────────────────────────────────

class FinancialRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="portfoliocompany.id")
    year: int
    quarter: int
    revenue: float
    ebitda: float
    net_debt: float

    company: Optional[PortfolioCompany] = Relationship(back_populates="financials")


# ── ESGMetric ─────────────────────────────────────────────────────────────────

class ESGMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="portfoliocompany.id")
    carbon_intensity: float
    energy_dependency_score: float
    supplier_concentration: float
    epc_rating: Optional[str] = None

    company: Optional[PortfolioCompany] = Relationship(back_populates="esg_metrics")


# ── MacroSignal ───────────────────────────────────────────────────────────────

class MacroSignal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="portfoliocompany.id")
    signal_type: str   # "CBAM_EXPOSURE" | "INTEREST_RATE_SENSITIVITY"
    level: str         # "high" | "medium" | "low" | "none"
    value: float       # numeric equivalent (0.0–1.0)
    description: str
    source_ref: str

    company: Optional[PortfolioCompany] = Relationship(back_populates="macro_signals")


# ── RiskFactor ────────────────────────────────────────────────────────────────

class RiskFactor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="portfoliocompany.id")
    factor_type: FactorType
    raw_source_ref: str
    normalized_value: float      # 0–100 (higher = worse)
    weight: float                # contribution within its parent composite (0–1)
    contributing_inputs: str     # JSON array of ContributingInput dicts
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    company: Optional[PortfolioCompany] = Relationship(back_populates="risk_factors")


# ── RiskAlert ─────────────────────────────────────────────────────────────────

class RiskAlert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="portfoliocompany.id")
    rule_name: str = Field(default="")
    severity: RiskSeverity
    category: str
    description: str
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    company: Optional[PortfolioCompany] = Relationship(back_populates="risk_alerts")


# ── PreInvestmentTarget ───────────────────────────────────────────────────────

class PreInvestmentTarget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    sector: str
    country: str
    # ESG inputs
    carbon_intensity: float
    energy_dependency_score: float
    supplier_concentration: float
    epc_rating: Optional[str] = None
    # Financial inputs
    revenue_em: float
    ebitda_em: float
    net_debt_em: float
    # Macro signal (CBAM level as string)
    cbam_level: str = "none"
    # IR sensitivity for RE targets
    ir_sensitivity: float = 0.5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Response schemas ──────────────────────────────────────────────────────────

class FundRead(SQLModel):
    id: int
    name: str
    country: str
    strategy: FundStrategy
    currency: str


class PortfolioCompanyRead(SQLModel):
    id: int
    fund_id: int
    name: str
    sector: str
    country: str
    entry_year: int


class FinancialRecordRead(SQLModel):
    id: int
    company_id: int
    year: int
    quarter: int
    revenue: float
    ebitda: float
    net_debt: float


class ESGMetricRead(SQLModel):
    id: int
    company_id: int
    carbon_intensity: float
    energy_dependency_score: float
    supplier_concentration: float
    epc_rating: Optional[str]


class MacroSignalRead(SQLModel):
    id: int
    company_id: int
    signal_type: str
    level: str
    value: float
    description: str
    source_ref: str


class RiskAlertRead(SQLModel):
    id: int
    company_id: int
    rule_name: str
    severity: RiskSeverity
    category: str
    description: str
    threshold_value: Optional[float]
    actual_value: Optional[float]
    created_at: datetime


class ContributingInput(SQLModel):
    source_table: str
    record_id: Optional[int]
    field: str
    raw_value: Optional[Any]
    unit: Optional[str]
    description: str


class RiskFactorRead(SQLModel):
    id: int
    company_id: int
    factor_type: FactorType
    raw_source_ref: str
    normalized_value: float
    weight: float
    contributing_inputs: list[ContributingInput]
    last_updated: datetime

    @classmethod
    def from_orm_with_json(cls, rf: "RiskFactor") -> "RiskFactorRead":
        inputs = json.loads(rf.contributing_inputs or "[]")
        return cls(
            id=rf.id,
            company_id=rf.company_id,
            factor_type=rf.factor_type,
            raw_source_ref=rf.raw_source_ref,
            normalized_value=rf.normalized_value,
            weight=rf.weight,
            contributing_inputs=[ContributingInput(**i) for i in inputs],
            last_updated=rf.last_updated,
        )


class RiskFactorLineage(SQLModel):
    risk_factor: RiskFactorRead
    transform_description: str
    composite_weight_pct: float


class PortfolioCompanyDetail(SQLModel):
    id: int
    fund_id: int
    name: str
    sector: str
    country: str
    entry_year: int
    financials: list[FinancialRecordRead] = []
    esg_metrics: list[ESGMetricRead] = []


class FundPortfolio(SQLModel):
    fund: FundRead
    companies: list[PortfolioCompanyRead] = []


# ── Commentary schemas ────────────────────────────────────────────────────────

class CommentarySentence(SQLModel):
    sentence: str
    source_refs: list[str]


class CommentaryResponse(SQLModel):
    available: bool
    company_id: int
    sentences: list[CommentarySentence]
    message: Optional[str] = None


# ── Screening schemas ─────────────────────────────────────────────────────────

class ScreeningInput(SQLModel):
    name: str
    sector: str
    country: str
    carbon_intensity: float
    energy_dependency_score: float
    supplier_concentration: float
    epc_rating: Optional[str] = None
    revenue_em: float
    ebitda_em: float
    net_debt_em: float
    cbam_level: str = "none"
    ir_sensitivity: float = 0.5


class ScreeningVerdict(SQLModel):
    name: str
    sector: str
    overall_score: float
    transition_score: float
    financial_score: float
    rag_flag: str          # "red" | "amber" | "green"
    top_factors: list[dict]
    alerts: list[dict]
    engine_note: str = "Same normalization + rules engine as portfolio monitoring"


# ── ROI schemas ───────────────────────────────────────────────────────────────

class RoiInput(SQLModel):
    portfolio_companies: int = 25
    hours_per_company_per_report: float = 12.0
    reports_per_year: int = 4
    analyst_rate_eur: float = 120.0
    tier: str = "growth"           # "starter" | "growth" | "enterprise"


class RoiResult(SQLModel):
    annual_hours_saved: float
    annual_eur_saved: float
    greencast_annual_cost: float
    net_saving: float
    payback_months: float
    payback_display: str
    tier: str
    tier_label: str
    inputs: RoiInput
