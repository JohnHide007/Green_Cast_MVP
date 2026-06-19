from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class FundStrategy(str, Enum):
    PE = "PE"
    PC = "PC"
    RE = "RE"


class RiskSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


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


# ── RiskAlert ─────────────────────────────────────────────────────────────────

class RiskAlert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="portfoliocompany.id")
    severity: RiskSeverity
    category: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    company: Optional[PortfolioCompany] = Relationship(back_populates="risk_alerts")


# ── Response schemas (no table=True) ─────────────────────────────────────────

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


class RiskAlertRead(SQLModel):
    id: int
    company_id: int
    severity: RiskSeverity
    category: str
    description: str
    created_at: datetime


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
