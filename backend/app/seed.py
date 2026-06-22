from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import (
    ESGMetric,
    FinancialRecord,
    Fund,
    FundStrategy,
    MacroSignal,
    PortfolioCompany,
)
from app.normalization import compute_risk_factors
from app.rules import evaluate_rules

FUNDS = [
    {"name": "Nordkap Private Credit I", "country": "NL", "strategy": FundStrategy.PC, "currency": "EUR"},
    {"name": "Rhein Residential Real Estate III", "country": "DE", "strategy": FundStrategy.RE, "currency": "EUR"},
    {"name": "Albion Capital Partners VI", "country": "GB", "strategy": FundStrategy.PE, "currency": "GBP"},
]

# (name, sector, country, entry_year)
COMPANIES = {
    "Nordkap Private Credit I": [
        ("Hanseatic Steel GmbH", "Metals & Mining", "DE", 2019),
        ("Benelux Logistics BV", "Logistics", "NL", 2020),
        ("Noord Chemie NV", "Chemicals", "NL", 2018),
        ("Rheintal Packaging GmbH", "Packaging", "DE", 2021),
        ("Baltic Freight Services AS", "Logistics", "EE", 2020),
        ("Eindhoven Precision Parts BV", "Manufacturing", "NL", 2019),
        ("Vistula Industrial Holdings", "Industrials", "PL", 2022),
        ("Antwerp Port Terminals NV", "Infrastructure", "BE", 2021),
    ],
    "Rhein Residential Real Estate III": [
        ("Berliner Wohnen GmbH", "Residential RE", "DE", 2018),
        ("Kölner Stadtquartier GmbH", "Residential RE", "DE", 2019),
        ("München Süd Wohnbau GmbH", "Residential RE", "DE", 2020),
        ("Hamburg Hafenviertel RE", "Residential RE", "DE", 2019),
        ("Dresden Altstadt Immobilien", "Residential RE", "DE", 2021),
        ("Frankfurt Westend Portfolio GmbH", "Mixed-Use RE", "DE", 2018),
        ("Leipzig Wohnpark GmbH", "Residential RE", "DE", 2022),
        ("Düsseldorf Rheinufer GmbH", "Residential RE", "DE", 2020),
        ("Stuttgart Mitte Residential", "Residential RE", "DE", 2021),
        ("Hannover City Living GmbH", "Residential RE", "DE", 2019),
        ("Nürnberg Südstadt Portfolio", "Residential RE", "DE", 2022),
        ("Bremen Harbour District RE", "Mixed-Use RE", "DE", 2021),
    ],
    "Albion Capital Partners VI": [
        ("Bristol Pharma Ltd", "Healthcare", "GB", 2019),
        ("Edinburgh Tech Solutions Ltd", "Software", "GB", 2020),
        ("Manchester Aerospace Components Ltd", "Aerospace", "GB", 2018),
        ("Cardiff Renewables Ltd", "Energy", "GB", 2021),
        ("Leeds Consumer Brands Group", "Consumer Goods", "GB", 2019),
        ("Oxford Biotech Holdings Ltd", "Biotech", "GB", 2022),
        ("Liverpool Port Logistics Ltd", "Logistics", "GB", 2020),
        ("Birmingham Advanced Manufacturing", "Manufacturing", "GB", 2021),
        ("Nottingham Digital Media Group", "Media", "GB", 2020),
        ("Sheffield Speciality Chemicals Ltd", "Chemicals", "GB", 2019),
    ],
}

# ESG seed data per company: (carbon_intensity, energy_dependency_score, supplier_concentration, epc_rating)
ESG_DATA: dict[str, tuple] = {
    # ── Nordkap (industrial / PC) ─────────────────────────────────────────────
    # Hanseatic Steel: high carbon + energy → will fire LEVERAGE_HIGH due to net_debt=250
    "Hanseatic Steel GmbH":               (312.4, 0.82, 0.61, None),
    "Benelux Logistics BV":               (88.3,  0.54, 0.38, None),
    "Noord Chemie NV":                    (241.7, 0.76, 0.55, None),
    "Rheintal Packaging GmbH":            (134.2, 0.49, 0.42, None),
    "Baltic Freight Services AS":         (102.6, 0.58, 0.33, None),
    "Eindhoven Precision Parts BV":       (78.9,  0.41, 0.29, None),
    "Vistula Industrial Holdings":        (198.1, 0.68, 0.52, None),
    "Antwerp Port Terminals NV":          (157.3, 0.63, 0.44, None),
    # ── Rhein RE ─────────────────────────────────────────────────────────────
    "Berliner Wohnen GmbH":               (42.1,  0.31, 0.12, "C"),
    "Kölner Stadtquartier GmbH":          (38.7,  0.28, 0.09, "B"),
    "München Süd Wohnbau GmbH":           (31.4,  0.24, 0.08, "B"),
    "Hamburg Hafenviertel RE":             (55.2,  0.36, 0.14, "D"),
    "Dresden Altstadt Immobilien":         (61.8,  0.39, 0.17, "D"),
    "Frankfurt Westend Portfolio GmbH":   (47.3,  0.33, 0.11, "C"),
    "Leipzig Wohnpark GmbH":              (35.9,  0.26, 0.10, "B"),
    "Düsseldorf Rheinufer GmbH":          (44.6,  0.31, 0.12, "C"),
    "Stuttgart Mitte Residential":         (29.8,  0.22, 0.07, "A"),
    "Hannover City Living GmbH":          (51.4,  0.34, 0.13, "C"),
    "Nürnberg Südstadt Portfolio":         (33.2,  0.25, 0.09, "B"),
    "Bremen Harbour District RE":          (67.5,  0.42, 0.18, "D"),
    # ── Albion PE ─────────────────────────────────────────────────────────────
    "Bristol Pharma Ltd":                 (54.8,  0.38, 0.31, None),
    "Edinburgh Tech Solutions Ltd":        (12.3,  0.14, 0.22, None),
    "Manchester Aerospace Components Ltd": (189.4, 0.72, 0.58, None),
    "Cardiff Renewables Ltd":             (8.7,   0.09, 0.19, None),
    "Leeds Consumer Brands Group":         (67.2,  0.44, 0.36, None),
    "Oxford Biotech Holdings Ltd":         (23.1,  0.18, 0.25, None),
    "Liverpool Port Logistics Ltd":        (94.6,  0.56, 0.41, None),
    "Birmingham Advanced Manufacturing":   (143.7, 0.62, 0.49, None),
    "Nottingham Digital Media Group":      (9.4,   0.11, 0.17, None),
    "Sheffield Speciality Chemicals Ltd":  (212.8, 0.74, 0.53, None),
}

# MacroSignals: list of (signal_type, level, value, description, source_ref)
MACRO_SIGNALS: dict[str, list[tuple]] = {
    # ── Nordkap (industrial) ─────────────────────────────────────────────────
    "Hanseatic Steel GmbH": [
        ("CBAM_EXPOSURE", "high", 0.85,
         "Steel manufacturing directly in scope for EU CBAM from 2026; "
         "embedded carbon costs pass through import levy on EU competitors.",
         "EU CBAM Regulation 2023/956, Annex I — iron & steel"),
    ],
    "Noord Chemie NV": [
        ("CBAM_EXPOSURE", "high", 0.85,
         "Bulk inorganic chemicals production in scope for EU CBAM Phase 1; "
         "carbon cost estimated at €3.1M/year at current EU ETS prices.",
         "EU CBAM Regulation 2023/956, Annex I — chemicals"),
    ],
    "Vistula Industrial Holdings": [
        ("CBAM_EXPOSURE", "medium", 0.55,
         "Mixed industrial production: ~40% of output falls under CBAM Annex I sectors. "
         "Partial exposure to carbon border levy from 2026.",
         "EU CBAM Regulation 2023/956, Annex I — partial scope"),
    ],
    "Antwerp Port Terminals NV": [
        ("CBAM_EXPOSURE", "low", 0.20,
         "Port terminal operations handle CBAM-covered goods but are not direct producers. "
         "Indirect exposure via shipper compliance cost pass-through.",
         "EU CBAM Regulation 2023/956 — indirect logistics exposure"),
    ],
    "Rheintal Packaging GmbH": [
        ("CBAM_EXPOSURE", "low", 0.20,
         "Packaging sector has indirect CBAM exposure via steel and aluminium input cost inflation. "
         "Not directly in scope as a producer.",
         "EU CBAM Regulation 2023/956 — upstream materials exposure"),
    ],
    # ── Rhein RE ─────────────────────────────────────────────────────────────
    "Berliner Wohnen GmbH": [
        ("INTEREST_RATE_SENSITIVITY", "high", 0.82,
         "High-LTV residential portfolio (67% floating-rate debt) "
         "with significant exposure to ECB rate trajectory. "
         "100bp rate rise adds ~€1.4M annual interest cost.",
         "ECB Monetary Policy Review — June 2025; internal debt covenant analysis"),
    ],
    "Kölner Stadtquartier GmbH": [
        ("INTEREST_RATE_SENSITIVITY", "medium", 0.60,
         "Mixed fixed/floating debt structure. 45% of debt linked to Euribor. "
         "Moderate sensitivity to rate path.",
         "ECB Monetary Policy Review — June 2025"),
    ],
    "München Süd Wohnbau GmbH": [
        ("INTEREST_RATE_SENSITIVITY", "medium", 0.55,
         "50% fixed-rate debt hedged through 2027; remainder floating. "
         "Rate risk partially mitigated by strong Munich rental market.",
         "ECB Monetary Policy Review — June 2025"),
    ],
    "Hamburg Hafenviertel RE": [
        ("INTEREST_RATE_SENSITIVITY", "high", 0.78,
         "EPC D asset with high refinancing risk: lenders applying green discount "
         "on below-C rated stock from 2026. Floating rate on 60% of debt.",
         "ECB Monetary Policy Review — June 2025; Hamburg lender green pricing data"),
    ],
    "Dresden Altstadt Immobilien": [
        ("INTEREST_RATE_SENSITIVITY", "high", 0.80,
         "EPC D portfolio in softer Dresden rental market. "
         "High floating-rate exposure (70%) coincides with pending retrofit capex.",
         "ECB Monetary Policy Review — June 2025"),
    ],
    "Frankfurt Westend Portfolio GmbH": [
        ("INTEREST_RATE_SENSITIVITY", "medium", 0.58,
         "Prime Frankfurt mixed-use; strong covenant mitigates rate risk. "
         "40% floating exposure.",
         "ECB Monetary Policy Review — June 2025"),
    ],
    "Leipzig Wohnpark GmbH": [
        ("INTEREST_RATE_SENSITIVITY", "medium", 0.52,
         "Newer portfolio with longer fixed-rate hedges; moderate floating exposure (35%).",
         "ECB Monetary Policy Review — June 2025"),
    ],
    "Düsseldorf Rheinufer GmbH": [
        ("INTEREST_RATE_SENSITIVITY", "medium", 0.62,
         "Riverside residential — strong demand but 48% floating debt. "
         "Moderate rate sensitivity.",
         "ECB Monetary Policy Review — June 2025"),
    ],
    "Stuttgart Mitte Residential": [
        ("INTEREST_RATE_SENSITIVITY", "low", 0.35,
         "EPC A-rated portfolio; lender green-pricing benefit offsets rate exposure. "
         "Predominantly fixed-rate debt.",
         "ECB Monetary Policy Review — June 2025; Stuttgart green mortgage data"),
    ],
    "Hannover City Living GmbH": [
        ("INTEREST_RATE_SENSITIVITY", "medium", 0.60,
         "Mid-tier residential with balanced fixed/floating mix.",
         "ECB Monetary Policy Review — June 2025"),
    ],
    "Nürnberg Südstadt Portfolio": [
        ("INTEREST_RATE_SENSITIVITY", "medium", 0.50,
         "Newer acquisitions with 3-year fixed hedges; below-average floating exposure.",
         "ECB Monetary Policy Review — June 2025"),
    ],
    "Bremen Harbour District RE": [
        ("INTEREST_RATE_SENSITIVITY", "high", 0.75,
         "EPC D mixed-use in flood-risk zone; insurance cost inflation combines "
         "with floating-rate debt (65%) to create elevated refinancing risk.",
         "ECB Monetary Policy Review — June 2025; Bremen flood-zone premium data"),
    ],
    # ── Albion PE ─────────────────────────────────────────────────────────────
    "Manchester Aerospace Components Ltd": [
        ("CBAM_EXPOSURE", "medium", 0.55,
         "Aerospace manufacturing uses aluminium and titanium alloys covered under UK ETS. "
         "UK–EU carbon price alignment risk adds to input cost uncertainty.",
         "UK ETS — aerospace sector; EU CBAM Regulation 2023/956 upstream linkage"),
    ],
    "Sheffield Speciality Chemicals Ltd": [
        ("CBAM_EXPOSURE", "high", 0.85,
         "Speciality chemicals with REACH-listed compounds and EU export exposure. "
         "High CBAM and regulatory compliance cost risk.",
         "EU CBAM Regulation 2023/956, Annex I; REACH SVHC candidate list 2024"),
    ],
    "Birmingham Advanced Manufacturing": [
        ("CBAM_EXPOSURE", "low", 0.20,
         "Advanced manufacturing with partial CBAM-covered material inputs (steel/aluminium). "
         "Not a direct CBAM-scope producer.",
         "EU CBAM Regulation 2023/956 — upstream materials exposure"),
    ],
}

# Quarterly financials: (base_rev_€m, base_ebitda_€m, net_debt_€m)
def _financials(base_rev: float, base_ebitda: float, base_debt: float) -> list[tuple]:
    records = []
    for yi, year in enumerate(range(2023, 2025)):
        for q in range(1, 5):
            growth = 1 + (yi * 4 + q - 1) * 0.008
            records.append((
                year, q,
                round(base_rev * growth, 2),
                round(base_ebitda * growth, 2),
                round(base_debt, 2),
            ))
    return records


FINANCIALS_BASE: dict[str, tuple] = {
    # Hanseatic Steel: net_debt raised to 250 → leverage ≈ 6.9× (HIGH) for demo contrast
    "Hanseatic Steel GmbH":               (48.2,  9.1,  250.0),
    "Benelux Logistics BV":               (31.6,  5.8,   62.0),
    "Noord Chemie NV":                    (62.4, 11.2,  198.0),
    "Rheintal Packaging GmbH":            (22.8,  4.3,   44.0),
    "Baltic Freight Services AS":         (18.3,  3.2,   35.0),
    "Eindhoven Precision Parts BV":       (27.1,  5.6,   51.0),
    "Vistula Industrial Holdings":        (41.5,  7.4,  121.0),
    "Antwerp Port Terminals NV":          (54.7,  9.8,  163.0),
    "Berliner Wohnen GmbH":               (14.2,  8.9,  212.0),
    "Kölner Stadtquartier GmbH":          (11.8,  7.4,  174.0),
    "München Süd Wohnbau GmbH":           (16.3, 10.2,  248.0),
    "Hamburg Hafenviertel RE":             (9.7,   6.1,  143.0),
    "Dresden Altstadt Immobilien":         (8.4,   5.3,  124.0),
    "Frankfurt Westend Portfolio GmbH":   (19.1, 11.9,  287.0),
    "Leipzig Wohnpark GmbH":              (7.6,   4.8,   98.0),
    "Düsseldorf Rheinufer GmbH":          (12.4,  7.8,  186.0),
    "Stuttgart Mitte Residential":         (10.8,  6.8,  162.0),
    "Hannover City Living GmbH":          (9.2,   5.8,  138.0),
    "Nürnberg Südstadt Portfolio":         (6.8,   4.3,   91.0),
    "Bremen Harbour District RE":          (11.3,  7.1,  169.0),
    "Bristol Pharma Ltd":                 (38.4,  9.6,   87.0),
    "Edinburgh Tech Solutions Ltd":        (22.7,  7.3,   31.0),
    "Manchester Aerospace Components Ltd": (51.3, 10.8,  138.0),
    "Cardiff Renewables Ltd":             (17.9,  6.4,   54.0),
    "Leeds Consumer Brands Group":         (44.2,  8.8,  102.0),
    "Oxford Biotech Holdings Ltd":         (12.1,  3.2,   28.0),
    "Liverpool Port Logistics Ltd":        (29.6,  5.9,   71.0),
    "Birmingham Advanced Manufacturing":   (36.8,  7.4,   98.0),
    "Nottingham Digital Media Group":      (18.4,  5.5,   22.0),
    "Sheffield Speciality Chemicals Ltd":  (43.7,  8.3,  117.0),
}


def seed(session: Session) -> None:
    existing = session.exec(select(Fund)).first()
    if existing:
        return

    for fund_data in FUNDS:
        fund = Fund(**fund_data)
        session.add(fund)
        session.flush()

        for name, sector, country, entry_year in COMPANIES[fund.name]:
            company = PortfolioCompany(
                fund_id=fund.id,
                name=name,
                sector=sector,
                country=country,
                entry_year=entry_year,
            )
            session.add(company)
            session.flush()

            carbon, energy, supplier, epc = ESG_DATA[name]
            esg = ESGMetric(
                company_id=company.id,
                carbon_intensity=carbon,
                energy_dependency_score=energy,
                supplier_concentration=supplier,
                epc_rating=epc,
            )
            session.add(esg)
            session.flush()

            macro_list: list[MacroSignal] = []
            for sig_type, level, value, description, source_ref in MACRO_SIGNALS.get(name, []):
                ms = MacroSignal(
                    company_id=company.id,
                    signal_type=sig_type,
                    level=level,
                    value=value,
                    description=description,
                    source_ref=source_ref,
                )
                session.add(ms)
                macro_list.append(ms)
            if macro_list:
                session.flush()

            financial_list: list[FinancialRecord] = []
            base_rev, base_ebitda, base_debt = FINANCIALS_BASE[name]
            for year, quarter, revenue, ebitda, net_debt in _financials(base_rev, base_ebitda, base_debt):
                fr = FinancialRecord(
                    company_id=company.id,
                    year=year,
                    quarter=quarter,
                    revenue=revenue,
                    ebitda=ebitda,
                    net_debt=net_debt,
                )
                session.add(fr)
                financial_list.append(fr)
            session.flush()

            # Rules engine generates alerts from raw inputs
            for alert in evaluate_rules(company, esg, financial_list, macro_list):
                session.add(alert)

            # Normalise all raw inputs into RiskFactor rows
            for rf in compute_risk_factors(company, esg, financial_list, macro_list):
                session.add(rf)

    session.commit()
