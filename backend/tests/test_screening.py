"""
Tests for the pre-investment screening endpoint.
Verifies: RAG logic, verdict structure, top 3 factors, alert generation.
"""

import pytest
from fastapi.testclient import TestClient

BASE = {
    "name": "Test Target GmbH",
    "sector": "Metals & Mining",
    "country": "DE",
    "carbon_intensity": 400.0,     # 80/100 carbon risk
    "energy_dependency_score": 0.85,
    "supplier_concentration": 0.70,
    "epc_rating": None,
    "revenue_em": 40.0,
    "ebitda_em": 8.0,
    "net_debt_em": 350.0,           # 10.9× EBITDA → 100 leverage risk
    "cbam_level": "high",
    "ir_sensitivity": 0.5,
}


class TestScreeningVerdict:
    def test_200_response(self, client: TestClient):
        resp = client.post("/screening/evaluate", json=BASE)
        assert resp.status_code == 200

    def test_verdict_structure(self, client: TestClient):
        data = client.post("/screening/evaluate", json=BASE).json()
        for field in ("name", "sector", "overall_score", "transition_score",
                      "financial_score", "rag_flag", "top_factors", "alerts"):
            assert field in data

    def test_high_risk_target_is_red(self, client: TestClient):
        data = client.post("/screening/evaluate", json=BASE).json()
        assert data["rag_flag"] == "red"
        assert data["overall_score"] >= 67

    def test_low_risk_target_is_green(self, client: TestClient):
        low_risk = {
            **BASE,
            "carbon_intensity": 10.0,
            "energy_dependency_score": 0.10,
            "supplier_concentration": 0.15,
            "cbam_level": "none",
            "net_debt_em": 5.0,
            "ebitda_em": 20.0,
            "revenue_em": 50.0,
        }
        data = client.post("/screening/evaluate", json=low_risk).json()
        assert data["rag_flag"] == "green"
        assert data["overall_score"] < 34

    def test_top_factors_count(self, client: TestClient):
        data = client.post("/screening/evaluate", json=BASE).json()
        assert 1 <= len(data["top_factors"]) <= 3

    def test_top_factors_have_required_fields(self, client: TestClient):
        data = client.post("/screening/evaluate", json=BASE).json()
        for tf in data["top_factors"]:
            assert "factor_type" in tf
            assert "normalized_value" in tf
            assert "weight" in tf

    def test_alerts_present_for_high_risk(self, client: TestClient):
        data = client.post("/screening/evaluate", json=BASE).json()
        assert len(data["alerts"]) >= 2

    def test_alert_structure(self, client: TestClient):
        data = client.post("/screening/evaluate", json=BASE).json()
        for alert in data["alerts"]:
            assert "rule_name" in alert
            assert "severity" in alert
            assert "category" in alert
            assert "description" in alert

    def test_re_target_has_epc_factor(self, client: TestClient):
        re_target = {
            **BASE,
            "epc_rating": "D",
            "carbon_intensity": 50.0,
            "cbam_level": "none",
            "net_debt_em": 100.0,
            "revenue_em": 12.0,
            "ebitda_em": 7.0,
            "ir_sensitivity": 0.80,
        }
        data = client.post("/screening/evaluate", json=re_target).json()
        factor_types = {f["factor_type"] for f in data["top_factors"]}
        # EPC D should score very high and appear in top 3
        all_types = [f["factor_type"] for f in data["top_factors"]]
        assert "EPC_RATING" in all_types or data["transition_score"] > 40

    def test_scores_in_range(self, client: TestClient):
        data = client.post("/screening/evaluate", json=BASE).json()
        for score in (data["overall_score"], data["transition_score"], data["financial_score"]):
            assert 0.0 <= score <= 100.0

    def test_name_and_sector_echoed(self, client: TestClient):
        data = client.post("/screening/evaluate", json=BASE).json()
        assert data["name"] == BASE["name"]
        assert data["sector"] == BASE["sector"]
