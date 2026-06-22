from fastapi.testclient import TestClient


def _first_company_id(client: TestClient) -> int:
    funds = client.get("/funds").json()
    portfolio = client.get(f"/funds/{funds[0]['id']}/portfolio").json()
    return portfolio["companies"][0]["id"]


def test_get_company_200(client: TestClient):
    company_id = _first_company_id(client)
    response = client.get(f"/portfolio/{company_id}")
    assert response.status_code == 200


def test_get_company_fields(client: TestClient):
    company_id = _first_company_id(client)
    data = client.get(f"/portfolio/{company_id}").json()
    for field in ("id", "fund_id", "name", "sector", "country", "entry_year", "financials", "esg_metrics"):
        assert field in data


def test_get_company_has_financials(client: TestClient):
    company_id = _first_company_id(client)
    data = client.get(f"/portfolio/{company_id}").json()
    # 2 years × 4 quarters = 8 records
    assert len(data["financials"]) == 8


def test_get_company_financial_fields(client: TestClient):
    company_id = _first_company_id(client)
    record = client.get(f"/portfolio/{company_id}").json()["financials"][0]
    for field in ("year", "quarter", "revenue", "ebitda", "net_debt"):
        assert field in record


def test_get_company_has_esg(client: TestClient):
    company_id = _first_company_id(client)
    data = client.get(f"/portfolio/{company_id}").json()
    assert len(data["esg_metrics"]) >= 1
    esg = data["esg_metrics"][0]
    for field in ("carbon_intensity", "energy_dependency_score", "supplier_concentration"):
        assert field in esg


def test_get_company_404(client: TestClient):
    response = client.get("/portfolio/9999")
    assert response.status_code == 404


def test_risk_alerts_200(client: TestClient):
    company_id = _first_company_id(client)
    response = client.get(f"/portfolio/{company_id}/risk-alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_risk_alerts_fields(client: TestClient):
    # Hanseatic Steel fires multiple rules: CARBON_INTENSITY_HIGH, ENERGY_DEPENDENCY_HIGH, CBAM_HIGH_EXPOSURE, LEVERAGE_HIGH
    funds = client.get("/funds").json()
    nordkap = next(f for f in funds if "Nordkap" in f["name"])
    companies = client.get(f"/funds/{nordkap['id']}/portfolio").json()["companies"]
    hanseatic = next(c for c in companies if "Hanseatic" in c["name"])

    alerts = client.get(f"/portfolio/{hanseatic['id']}/risk-alerts").json()
    assert len(alerts) >= 2
    for alert in alerts:
        for field in ("id", "company_id", "severity", "category", "description", "rule_name", "created_at"):
            assert field in alert


def test_risk_alerts_404(client: TestClient):
    response = client.get("/portfolio/9999/risk-alerts")
    assert response.status_code == 404


def test_hanseatic_has_leverage_alert(client: TestClient):
    """Hanseatic Steel (net_debt=250, annual EBITDA~36) → leverage ~6.9× → LEVERAGE_HIGH fires."""
    funds = client.get("/funds").json()
    nordkap = next(f for f in funds if "Nordkap" in f["name"])
    companies = client.get(f"/funds/{nordkap['id']}/portfolio").json()["companies"]
    hanseatic = next(c for c in companies if "Hanseatic" in c["name"])

    alerts = client.get(f"/portfolio/{hanseatic['id']}/risk-alerts").json()
    rule_names = {a["rule_name"] for a in alerts}
    assert "LEVERAGE_HIGH" in rule_names


def test_risk_factors_three_composites(client: TestClient):
    """Every company must have all 3 composites."""
    company_id = _first_company_id(client)
    factors = client.get(f"/portfolio/{company_id}/risk-factors").json()
    types = {f["factor_type"] for f in factors}
    assert "OVERALL_RISK_SCORE" in types
    assert "TRANSITION_RISK_COMPOSITE" in types
    assert "FINANCIAL_RISK_COMPOSITE" in types


def test_risk_factors_overall_first(client: TestClient):
    """OVERALL_RISK_SCORE must be the first factor returned."""
    company_id = _first_company_id(client)
    factors = client.get(f"/portfolio/{company_id}/risk-factors").json()
    assert factors[0]["factor_type"] == "OVERALL_RISK_SCORE"
