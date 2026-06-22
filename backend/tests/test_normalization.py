"""
Tests for normalization transforms and the lineage endpoint.
Verifies:
  - Each individual transform produces correct scores
  - compute_risk_factors returns all expected factor types for industrial + RE
  - All 3 composites are present (TRANSITION, FINANCIAL, OVERALL)
  - Weight dicts each sum to 1.0
  - OVERALL_RISK_SCORE is returned first by /portfolio/{id}/risk-factors
  - Lineage endpoint returns transform_description and contributing_inputs
"""

import json

import pytest
from fastapi.testclient import TestClient

from app.normalization import (
    TR_WEIGHTS_INDUSTRIAL,
    TR_WEIGHTS_RE,
    FR_WEIGHTS_INDUSTRIAL,
    FR_WEIGHTS_RE,
    norm_carbon,
    norm_cbam,
    norm_ebitda_margin,
    norm_epc,
    norm_energy,
    norm_interest_rate,
    norm_ltv_re,
    norm_leverage_industrial,
    norm_supplier,
    compute_risk_factors,
)
from app.models import (
    ESGMetric,
    FactorType,
    FinancialRecord,
    MacroSignal,
    PortfolioCompany,
)


# ── Transform unit tests ──────────────────────────────────────────────────────

class TestNormCarbon:
    def test_zero_is_zero(self):
        assert norm_carbon(0.0) == 0.0

    def test_500_is_100(self):
        assert norm_carbon(500.0) == 100.0

    def test_capped_above_500(self):
        assert norm_carbon(600.0) == 100.0

    def test_midpoint(self):
        assert norm_carbon(250.0) == 50.0

    def test_typical_steel(self):
        assert norm_carbon(312.4) == pytest.approx(62.48, rel=1e-3)


class TestNormEnergy:
    def test_zero(self):
        assert norm_energy(0.0) == 0.0

    def test_one_is_100(self):
        assert norm_energy(1.0) == 100.0

    def test_midpoint(self):
        assert norm_energy(0.5) == 50.0

    def test_typical(self):
        assert norm_energy(0.82) == pytest.approx(82.0, rel=1e-3)


class TestNormSupplier:
    def test_zero(self):
        assert norm_supplier(0.0) == 0.0

    def test_one(self):
        assert norm_supplier(1.0) == 100.0

    def test_typical(self):
        assert norm_supplier(0.61) == pytest.approx(61.0, rel=1e-3)


class TestNormEpc:
    def test_a_is_lowest_risk(self):
        assert norm_epc("A") == 5.0

    def test_d_is_high_risk(self):
        assert norm_epc("D") == 70.0

    def test_g_is_max(self):
        assert norm_epc("G") == 100.0

    def test_case_insensitive(self):
        assert norm_epc("b") == norm_epc("B") == 20.0


class TestNormCbam:
    def test_none(self):
        assert norm_cbam("none") == 0.0

    def test_high(self):
        assert norm_cbam("high") == 85.0

    def test_medium(self):
        assert norm_cbam("medium") == 55.0

    def test_low(self):
        assert norm_cbam("low") == 20.0


class TestNormLtvRe:
    def test_zero_debt_is_zero(self):
        assert norm_ltv_re(0.0, 100.0) == 0.0

    def test_10x_is_100(self):
        assert norm_ltv_re(100.0, 10.0) == 100.0

    def test_capped(self):
        assert norm_ltv_re(1000.0, 10.0) == 100.0

    def test_typical_re(self):
        # net_debt=212, annual_rev=14.2*4=56.8 → LTV=3.73× → 37.3/100
        assert norm_ltv_re(212.0, 56.8) == pytest.approx(37.32, rel=1e-2)

    def test_zero_revenue(self):
        assert norm_ltv_re(100.0, 0.0) == 100.0


class TestNormLeverageIndustrial:
    def test_zero_debt_is_zero(self):
        assert norm_leverage_industrial(0.0, 50.0) == 0.0

    def test_8x_is_100(self):
        # 8× EBITDA → score 100
        assert norm_leverage_industrial(400.0, 50.0) == 100.0

    def test_capped(self):
        assert norm_leverage_industrial(1000.0, 50.0) == 100.0

    def test_typical_hanseatic(self):
        # net_debt=250, annual_ebitda=9.1*4=36.4 → 6.87× → 85.9
        result = norm_leverage_industrial(250.0, 36.4)
        assert 80.0 < result <= 100.0

    def test_zero_ebitda(self):
        assert norm_leverage_industrial(100.0, 0.0) == 100.0


class TestNormEbitdaMargin:
    def test_high_margin_is_low_risk(self):
        result = norm_ebitda_margin(30.0, 100.0)
        assert result == pytest.approx(0.0, abs=0.5)

    def test_zero_margin_is_100(self):
        assert norm_ebitda_margin(0.0, 100.0) == pytest.approx(100.0, abs=1.0)

    def test_negative_ebitda(self):
        assert norm_ebitda_margin(-10.0, 100.0) == 100.0

    def test_zero_revenue(self):
        assert norm_ebitda_margin(5.0, 0.0) == 100.0


class TestNormInterestRate:
    def test_zero(self):
        assert norm_interest_rate(0.0) == 0.0

    def test_one_is_100(self):
        assert norm_interest_rate(1.0) == 100.0

    def test_typical_high(self):
        assert norm_interest_rate(0.82) == pytest.approx(82.0, rel=1e-3)


# ── Weight profile tests ──────────────────────────────────────────────────────

class TestWeightProfiles:
    def test_tr_industrial_weights_sum_to_one(self):
        assert abs(sum(TR_WEIGHTS_INDUSTRIAL.values()) - 1.0) < 1e-9

    def test_tr_re_weights_sum_to_one(self):
        assert abs(sum(TR_WEIGHTS_RE.values()) - 1.0) < 1e-9

    def test_fr_industrial_weights_sum_to_one(self):
        assert abs(sum(FR_WEIGHTS_INDUSTRIAL.values()) - 1.0) < 1e-9

    def test_fr_re_weights_sum_to_one(self):
        assert abs(sum(FR_WEIGHTS_RE.values()) - 1.0) < 1e-9

    def test_re_cbam_is_small(self):
        # RE profile: CBAM ≈ 0 (max 5%)
        cbam_w = TR_WEIGHTS_RE.get(FactorType.CBAM_EXPOSURE, 0.0)
        assert cbam_w <= 0.10

    def test_re_epc_is_dominant(self):
        epc_w = TR_WEIGHTS_RE.get(FactorType.EPC_RATING, 0.0)
        assert epc_w >= 0.40

    def test_industrial_no_epc(self):
        assert FactorType.EPC_RATING not in TR_WEIGHTS_INDUSTRIAL

    def test_industrial_cbam_is_material(self):
        cbam_w = TR_WEIGHTS_INDUSTRIAL.get(FactorType.CBAM_EXPOSURE, 0.0)
        assert cbam_w >= 0.15


# ── compute_risk_factors integration tests ───────────────────────────────────

def _make_company() -> PortfolioCompany:
    return PortfolioCompany(
        id=1, fund_id=1, name="Test Co", sector="Test", country="DE", entry_year=2020,
    )


def _make_esg(is_re: bool = False) -> ESGMetric:
    return ESGMetric(
        id=10, company_id=1,
        carbon_intensity=200.0,
        energy_dependency_score=0.6,
        supplier_concentration=0.4,
        epc_rating="C" if is_re else None,
    )


def _make_financials() -> list[FinancialRecord]:
    return [
        FinancialRecord(id=100, company_id=1, year=2024, quarter=4,
                        revenue=25.0, ebitda=5.0, net_debt=80.0),
    ]


def _make_macro_cbam() -> list[MacroSignal]:
    return [
        MacroSignal(id=200, company_id=1, signal_type="CBAM_EXPOSURE",
                    level="medium", value=0.55,
                    description="Medium CBAM", source_ref="EU CBAM 2023/956"),
    ]


def _make_macro_re() -> list[MacroSignal]:
    return [
        MacroSignal(id=201, company_id=1, signal_type="INTEREST_RATE_SENSITIVITY",
                    level="high", value=0.80,
                    description="High rate sensitivity", source_ref="ECB MPR 2025"),
    ]


class TestComputeRiskFactors:
    def test_three_composites_always_present(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(), _make_financials(), _make_macro_cbam()
        )
        types = {f.factor_type for f in factors}
        assert FactorType.OVERALL_RISK_SCORE in types
        assert FactorType.TRANSITION_RISK_COMPOSITE in types
        assert FactorType.FINANCIAL_RISK_COMPOSITE in types

    def test_industrial_factor_types(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(), _make_financials(), _make_macro_cbam()
        )
        types = {f.factor_type for f in factors}
        for ft in (FactorType.CARBON_INTENSITY, FactorType.ENERGY_DEPENDENCY,
                   FactorType.SUPPLIER_CONCENTRATION, FactorType.CBAM_EXPOSURE,
                   FactorType.LEVERAGE_RATIO, FactorType.EBITDA_MARGIN):
            assert ft in types, f"{ft} missing from industrial factors"
        # RE-only factors must not appear
        assert FactorType.EPC_RATING not in types
        assert FactorType.INTEREST_RATE_SENSITIVITY not in types
        assert FactorType.LTV_RATIO not in types

    def test_re_factor_types(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(True), _make_financials(), _make_macro_re()
        )
        types = {f.factor_type for f in factors}
        assert FactorType.EPC_RATING in types
        assert FactorType.INTEREST_RATE_SENSITIVITY in types
        assert FactorType.LTV_RATIO in types
        # Industrial-only should not appear
        assert FactorType.LEVERAGE_RATIO not in types

    def test_overall_weight_is_one(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(), _make_financials(), []
        )
        overall = next(f for f in factors if f.factor_type == FactorType.OVERALL_RISK_SCORE)
        assert overall.weight == pytest.approx(1.0)

    def test_overall_value_within_bounds(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(), _make_financials(), _make_macro_cbam()
        )
        overall = next(f for f in factors if f.factor_type == FactorType.OVERALL_RISK_SCORE)
        assert 0.0 <= overall.normalized_value <= 100.0

    def test_contributing_inputs_parseable(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(), _make_financials(), _make_macro_cbam()
        )
        for factor in factors:
            parsed = json.loads(factor.contributing_inputs)
            assert isinstance(parsed, list)
            assert len(parsed) > 0
            for inp in parsed:
                assert "source_table" in inp
                assert "field" in inp
                assert "description" in inp

    def test_no_financials_skips_leverage_and_ebitda(self):
        factors = compute_risk_factors(_make_company(), _make_esg(), [], [])
        types = {f.factor_type for f in factors}
        assert FactorType.LEVERAGE_RATIO not in types
        assert FactorType.EBITDA_MARGIN not in types
        assert FactorType.LTV_RATIO not in types

    def test_tr_composite_weight_matches_overall(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(), _make_financials(), []
        )
        tr = next(f for f in factors if f.factor_type == FactorType.TRANSITION_RISK_COMPOSITE)
        # Industrial TR weight should be 0.65
        assert tr.weight == pytest.approx(0.65)

    def test_fr_composite_weight_matches_overall(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(), _make_financials(), []
        )
        fr = next(f for f in factors if f.factor_type == FactorType.FINANCIAL_RISK_COMPOSITE)
        # Industrial FR weight should be 0.35
        assert fr.weight == pytest.approx(0.35)

    def test_re_tr_composite_weight(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(True), _make_financials(), _make_macro_re()
        )
        tr = next(f for f in factors if f.factor_type == FactorType.TRANSITION_RISK_COMPOSITE)
        assert tr.weight == pytest.approx(0.45)

    def test_re_fr_composite_weight(self):
        factors = compute_risk_factors(
            _make_company(), _make_esg(True), _make_financials(), _make_macro_re()
        )
        fr = next(f for f in factors if f.factor_type == FactorType.FINANCIAL_RISK_COMPOSITE)
        assert fr.weight == pytest.approx(0.55)


# ── Lineage endpoint tests ────────────────────────────────────────────────────

class TestLineageEndpoint:
    def test_lineage_returns_200(self, client: TestClient):
        funds_resp = client.get("/funds")
        fund_id = funds_resp.json()[0]["id"]
        portfolio_resp = client.get(f"/funds/{fund_id}/portfolio")
        company_id = portfolio_resp.json()["companies"][0]["id"]

        factors_resp = client.get(f"/portfolio/{company_id}/risk-factors")
        assert factors_resp.status_code == 200
        factors = factors_resp.json()
        assert len(factors) > 0

        factor_id = factors[0]["id"]
        lineage_resp = client.get(f"/risk-factors/{factor_id}/lineage")
        assert lineage_resp.status_code == 200

    def test_lineage_structure(self, client: TestClient):
        funds_resp = client.get("/funds")
        fund_id = funds_resp.json()[0]["id"]
        portfolio_resp = client.get(f"/funds/{fund_id}/portfolio")
        company_id = portfolio_resp.json()["companies"][0]["id"]

        factors = client.get(f"/portfolio/{company_id}/risk-factors").json()
        factor_id = factors[0]["id"]

        data = client.get(f"/risk-factors/{factor_id}/lineage").json()
        assert "risk_factor" in data
        assert "transform_description" in data
        assert "composite_weight_pct" in data
        assert len(data["transform_description"]) > 10

    def test_lineage_contributing_inputs_non_empty(self, client: TestClient):
        funds_resp = client.get("/funds")
        fund_id = funds_resp.json()[0]["id"]
        companies = client.get(f"/funds/{fund_id}/portfolio").json()["companies"]
        company_id = companies[0]["id"]

        factors = client.get(f"/portfolio/{company_id}/risk-factors").json()
        for factor in factors:
            lineage = client.get(f"/risk-factors/{factor['id']}/lineage").json()
            inputs = lineage["risk_factor"]["contributing_inputs"]
            assert len(inputs) >= 1
            for inp in inputs:
                assert "source_table" in inp
                assert "description" in inp

    def test_lineage_source_refs_resolve_to_real_factor_types(self, client: TestClient):
        valid_types = {ft.value for ft in FactorType}
        funds_resp = client.get("/funds")
        fund_id = funds_resp.json()[0]["id"]
        companies = client.get(f"/funds/{fund_id}/portfolio").json()["companies"]
        company_id = companies[0]["id"]

        factors = client.get(f"/portfolio/{company_id}/risk-factors").json()
        for factor in factors:
            assert factor["factor_type"] in valid_types

    def test_lineage_404_for_missing_factor(self, client: TestClient):
        resp = client.get("/risk-factors/99999/lineage")
        assert resp.status_code == 404

    def test_risk_factors_overall_composite_first(self, client: TestClient):
        """OVERALL_RISK_SCORE must be the first factor returned."""
        funds_resp = client.get("/funds")
        fund_id = funds_resp.json()[0]["id"]
        companies = client.get(f"/funds/{fund_id}/portfolio").json()["companies"]
        company_id = companies[0]["id"]

        factors = client.get(f"/portfolio/{company_id}/risk-factors").json()
        assert factors[0]["factor_type"] == FactorType.OVERALL_RISK_SCORE.value

    def test_risk_factors_all_three_composites_present(self, client: TestClient):
        funds_resp = client.get("/funds")
        fund_id = funds_resp.json()[0]["id"]
        companies = client.get(f"/funds/{fund_id}/portfolio").json()["companies"]
        company_id = companies[0]["id"]

        factors = client.get(f"/portfolio/{company_id}/risk-factors").json()
        types = {f["factor_type"] for f in factors}
        assert FactorType.OVERALL_RISK_SCORE.value in types
        assert FactorType.TRANSITION_RISK_COMPOSITE.value in types
        assert FactorType.FINANCIAL_RISK_COMPOSITE.value in types

    def test_all_thirty_companies_have_risk_factors(self, client: TestClient):
        """Every seeded company must have risk factors."""
        funds = client.get("/funds").json()
        for fund in funds:
            companies = client.get(f"/funds/{fund['id']}/portfolio").json()["companies"]
            for company in companies:
                factors = client.get(f"/portfolio/{company['id']}/risk-factors").json()
                assert len(factors) > 0, f"No risk factors for company {company['name']}"
