from datetime import datetime

from sqlmodel import Session, select

from app.models import (
    ESGMetric,
    FinancialRecord,
    Fund,
    FundStrategy,
    PortfolioCompany,
    RiskAlert,
    RiskSeverity,
)

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

# ESG seed data per company (carbon_intensity, energy_dependency_score, supplier_concentration, epc_rating)
ESG_DATA = {
    "Hanseatic Steel GmbH":              (312.4, 0.82, 0.61, None),
    "Benelux Logistics BV":              (88.3,  0.54, 0.38, None),
    "Noord Chemie NV":                   (241.7, 0.76, 0.55, None),
    "Rheintal Packaging GmbH":           (134.2, 0.49, 0.42, None),
    "Baltic Freight Services AS":        (102.6, 0.58, 0.33, None),
    "Eindhoven Precision Parts BV":      (78.9,  0.41, 0.29, None),
    "Vistula Industrial Holdings":       (198.1, 0.68, 0.52, None),
    "Antwerp Port Terminals NV":         (157.3, 0.63, 0.44, None),
    "Berliner Wohnen GmbH":              (42.1,  0.31, 0.12, "C"),
    "Kölner Stadtquartier GmbH":         (38.7,  0.28, 0.09, "B"),
    "München Süd Wohnbau GmbH":          (31.4,  0.24, 0.08, "B"),
    "Hamburg Hafenviertel RE":            (55.2,  0.36, 0.14, "D"),
    "Dresden Altstadt Immobilien":        (61.8,  0.39, 0.17, "D"),
    "Frankfurt Westend Portfolio GmbH":  (47.3,  0.33, 0.11, "C"),
    "Leipzig Wohnpark GmbH":             (35.9,  0.26, 0.10, "B"),
    "Düsseldorf Rheinufer GmbH":         (44.6,  0.31, 0.12, "C"),
    "Stuttgart Mitte Residential":        (29.8,  0.22, 0.07, "A"),
    "Hannover City Living GmbH":         (51.4,  0.34, 0.13, "C"),
    "Nürnberg Südstadt Portfolio":        (33.2,  0.25, 0.09, "B"),
    "Bremen Harbour District RE":         (67.5,  0.42, 0.18, "D"),
    "Bristol Pharma Ltd":                (54.8,  0.38, 0.31, None),
    "Edinburgh Tech Solutions Ltd":       (12.3,  0.14, 0.22, None),
    "Manchester Aerospace Components Ltd":(189.4, 0.72, 0.58, None),
    "Cardiff Renewables Ltd":            (8.7,   0.09, 0.19, None),
    "Leeds Consumer Brands Group":        (67.2,  0.44, 0.36, None),
    "Oxford Biotech Holdings Ltd":        (23.1,  0.18, 0.25, None),
    "Liverpool Port Logistics Ltd":       (94.6,  0.56, 0.41, None),
    "Birmingham Advanced Manufacturing":  (143.7, 0.62, 0.49, None),
    "Nottingham Digital Media Group":     (9.4,   0.11, 0.17, None),
    "Sheffield Speciality Chemicals Ltd": (212.8, 0.74, 0.53, None),
}

# Quarterly financial records per company: (year, quarter, revenue_m, ebitda_m, net_debt_m)
def _financials(base_rev: float, base_ebitda: float, base_debt: float) -> list[tuple]:
    records = []
    for yi, year in enumerate(range(2023, 2025)):
        for q in range(1, 5):
            growth = 1 + (yi * 4 + q - 1) * 0.008
            records.append((year, q, round(base_rev * growth, 2),
                             round(base_ebitda * growth, 2), round(base_debt, 2)))
    return records


FINANCIALS_BASE = {
    "Hanseatic Steel GmbH":              (48.2,  9.1,  142.0),
    "Benelux Logistics BV":              (31.6,  5.8,   62.0),
    "Noord Chemie NV":                   (62.4, 11.2,  198.0),
    "Rheintal Packaging GmbH":           (22.8,  4.3,   44.0),
    "Baltic Freight Services AS":        (18.3,  3.2,   35.0),
    "Eindhoven Precision Parts BV":      (27.1,  5.6,   51.0),
    "Vistula Industrial Holdings":       (41.5,  7.4,  121.0),
    "Antwerp Port Terminals NV":         (54.7,  9.8,  163.0),
    "Berliner Wohnen GmbH":              (14.2,  8.9,  212.0),
    "Kölner Stadtquartier GmbH":         (11.8,  7.4,  174.0),
    "München Süd Wohnbau GmbH":          (16.3,  10.2, 248.0),
    "Hamburg Hafenviertel RE":            (9.7,   6.1,  143.0),
    "Dresden Altstadt Immobilien":        (8.4,   5.3,  124.0),
    "Frankfurt Westend Portfolio GmbH":  (19.1,  11.9, 287.0),
    "Leipzig Wohnpark GmbH":             (7.6,   4.8,   98.0),
    "Düsseldorf Rheinufer GmbH":         (12.4,  7.8,  186.0),
    "Stuttgart Mitte Residential":        (10.8,  6.8,  162.0),
    "Hannover City Living GmbH":         (9.2,   5.8,  138.0),
    "Nürnberg Südstadt Portfolio":        (6.8,   4.3,   91.0),
    "Bremen Harbour District RE":         (11.3,  7.1,  169.0),
    "Bristol Pharma Ltd":                (38.4,  9.6,   87.0),
    "Edinburgh Tech Solutions Ltd":       (22.7,  7.3,   31.0),
    "Manchester Aerospace Components Ltd":(51.3, 10.8,  138.0),
    "Cardiff Renewables Ltd":            (17.9,  6.4,   54.0),
    "Leeds Consumer Brands Group":        (44.2,  8.8,  102.0),
    "Oxford Biotech Holdings Ltd":        (12.1,  3.2,   28.0),
    "Liverpool Port Logistics Ltd":       (29.6,  5.9,   71.0),
    "Birmingham Advanced Manufacturing":  (36.8,  7.4,   98.0),
    "Nottingham Digital Media Group":     (18.4,  5.5,   22.0),
    "Sheffield Speciality Chemicals Ltd": (43.7,  8.3,  117.0),
}

RISK_ALERTS = {
    "Hanseatic Steel GmbH": [
        (RiskSeverity.high, "Carbon Regulation", "Carbon intensity (312 tCO2e/€M) exceeds EU ETS Phase 4 threshold. Cost impact estimated €4.2M annually under current pricing."),
        (RiskSeverity.medium, "Energy Dependency", "82% energy dependency on grid electricity exposes margins to wholesale power price volatility."),
    ],
    "Noord Chemie NV": [
        (RiskSeverity.high, "CSRD Compliance", "Scope 3 emissions not yet tracked. CSRD reporting obligation kicks in FY2025."),
        (RiskSeverity.medium, "Supply Chain", "Supplier concentration at 55% — top 3 suppliers account for majority of raw material supply."),
    ],
    "Vistula Industrial Holdings": [
        (RiskSeverity.medium, "Carbon Regulation", "Carbon intensity trending upward (+12% YoY). Exceeds sector median by 31%."),
    ],
    "Hamburg Hafenviertel RE": [
        (RiskSeverity.high, "EPC Rating", "EPC D rating triggers mandatory renovation requirement under EU Energy Performance of Buildings Directive by 2030."),
        (RiskSeverity.medium, "Stranded Asset Risk", "Below-par energy rating risks tenant flight to green-certified stock in tightening Hamburg rental market."),
    ],
    "Dresden Altstadt Immobilien": [
        (RiskSeverity.high, "EPC Rating", "EPC D rating. Retrofit cost estimated at €2.8M to reach C compliance target."),
    ],
    "Bremen Harbour District RE": [
        (RiskSeverity.medium, "Flood Risk", "Located in Zone IIa flood-risk corridor. Insurance premiums up 34% YoY."),
        (RiskSeverity.low, "EPC Rating", "EPC D — marginal compliance risk under current EPBD trajectory."),
    ],
    "Manchester Aerospace Components Ltd": [
        (RiskSeverity.high, "Carbon Regulation", "UK ETS exposure significant. Carbon intensity at 189 tCO2e/€M, sector average 120."),
        (RiskSeverity.medium, "Supply Chain", "58% supplier concentration in titanium supply chain — single-source risk for key alloy grade."),
    ],
    "Sheffield Speciality Chemicals Ltd": [
        (RiskSeverity.high, "REACH Compliance", "Two key compounds flagged under REACH SVHC candidate list update. Substitution cost projected £1.9M."),
        (RiskSeverity.high, "Carbon Regulation", "Carbon intensity at 213 tCO2e/€M — top decile for chemicals sector under UK ETS."),
    ],
    "Birmingham Advanced Manufacturing": [
        (RiskSeverity.medium, "Energy Dependency", "62% grid energy dependency. Unhedged exposure to UK electricity forward curve."),
    ],
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
            session.add(ESGMetric(
                company_id=company.id,
                carbon_intensity=carbon,
                energy_dependency_score=energy,
                supplier_concentration=supplier,
                epc_rating=epc,
            ))

            base_rev, base_ebitda, base_debt = FINANCIALS_BASE[name]
            for year, quarter, revenue, ebitda, net_debt in _financials(base_rev, base_ebitda, base_debt):
                session.add(FinancialRecord(
                    company_id=company.id,
                    year=year,
                    quarter=quarter,
                    revenue=revenue,
                    ebitda=ebitda,
                    net_debt=net_debt,
                ))

            for severity, category, description in RISK_ALERTS.get(name, []):
                session.add(RiskAlert(
                    company_id=company.id,
                    severity=severity,
                    category=category,
                    description=description,
                    created_at=datetime.utcnow(),
                ))

    session.commit()
