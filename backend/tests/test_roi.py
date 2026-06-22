"""
Tests for the ROI calculator endpoint.
Verifies: default payback < 3 months, tier pricing, output structure.
"""

from fastapi.testclient import TestClient

DEFAULTS = {
    "portfolio_companies": 25,
    "hours_per_company_per_report": 12.0,
    "reports_per_year": 4,
    "analyst_rate_eur": 120.0,
    "tier": "growth",
}


class TestRoiCalculator:
    def test_200_response(self, client: TestClient):
        resp = client.post("/roi/calculate", json=DEFAULTS)
        assert resp.status_code == 200

    def test_default_payback_under_one_quarter(self, client: TestClient):
        """Demo requirement: defaults must yield payback < 3 months."""
        data = client.post("/roi/calculate", json=DEFAULTS).json()
        assert data["payback_months"] < 3.0

    def test_output_structure(self, client: TestClient):
        data = client.post("/roi/calculate", json=DEFAULTS).json()
        for field in ("annual_hours_saved", "annual_eur_saved", "greencast_annual_cost",
                      "net_saving", "payback_months", "payback_display", "tier", "tier_label"):
            assert field in data

    def test_annual_saving_positive(self, client: TestClient):
        data = client.post("/roi/calculate", json=DEFAULTS).json()
        assert data["annual_eur_saved"] > 0

    def test_net_saving_positive_at_growth(self, client: TestClient):
        data = client.post("/roi/calculate", json=DEFAULTS).json()
        assert data["net_saving"] > 0

    def test_starter_tier_lower_cost(self, client: TestClient):
        starter = {**DEFAULTS, "tier": "starter"}
        growth = {**DEFAULTS, "tier": "growth"}
        s_data = client.post("/roi/calculate", json=starter).json()
        g_data = client.post("/roi/calculate", json=growth).json()
        assert s_data["greencast_annual_cost"] < g_data["greencast_annual_cost"]

    def test_enterprise_tier(self, client: TestClient):
        ent = {**DEFAULTS, "tier": "enterprise"}
        data = client.post("/roi/calculate", json=ent).json()
        assert data["greencast_annual_cost"] == 48_000.0

    def test_inputs_echoed(self, client: TestClient):
        data = client.post("/roi/calculate", json=DEFAULTS).json()
        assert data["inputs"]["portfolio_companies"] == 25
        assert data["inputs"]["tier"] == "growth"

    def test_payback_display_is_string(self, client: TestClient):
        data = client.post("/roi/calculate", json=DEFAULTS).json()
        assert isinstance(data["payback_display"], str)

    def test_invalid_tier_falls_back_to_growth(self, client: TestClient):
        bad = {**DEFAULTS, "tier": "unicorn"}
        data = client.post("/roi/calculate", json=bad).json()
        assert data["tier"] == "growth"
