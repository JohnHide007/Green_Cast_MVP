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
    # Hanseatic Steel has seeded alerts — find it
    funds = client.get("/funds").json()
    nordkap = next(f for f in funds if "Nordkap" in f["name"])
    companies = client.get(f"/funds/{nordkap['id']}/portfolio").json()["companies"]
    hanseatic = next(c for c in companies if "Hanseatic" in c["name"])

    alerts = client.get(f"/portfolio/{hanseatic['id']}/risk-alerts").json()
    assert len(alerts) == 2
    for alert in alerts:
        for field in ("id", "company_id", "severity", "category", "description", "created_at"):
            assert field in alert


def test_risk_alerts_404(client: TestClient):
    response = client.get("/portfolio/9999/risk-alerts")
    assert response.status_code == 404
