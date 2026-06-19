from fastapi.testclient import TestClient


def test_list_funds_returns_three(client: TestClient):
    response = client.get("/funds")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_funds_fields(client: TestClient):
    response = client.get("/funds")
    fund = response.json()[0]
    for field in ("id", "name", "country", "strategy", "currency"):
        assert field in fund


def test_fund_strategies_present(client: TestClient):
    strategies = {f["strategy"] for f in client.get("/funds").json()}
    assert strategies == {"PE", "PC", "RE"}


def test_fund_portfolio_nordkap(client: TestClient):
    funds = client.get("/funds").json()
    nordkap = next(f for f in funds if "Nordkap" in f["name"])

    response = client.get(f"/funds/{nordkap['id']}/portfolio")
    assert response.status_code == 200
    data = response.json()

    assert data["fund"]["id"] == nordkap["id"]
    assert len(data["companies"]) == 8


def test_fund_portfolio_rhein(client: TestClient):
    funds = client.get("/funds").json()
    rhein = next(f for f in funds if "Rhein" in f["name"])

    response = client.get(f"/funds/{rhein['id']}/portfolio")
    assert response.status_code == 200
    assert len(response.json()["companies"]) == 12


def test_fund_portfolio_albion(client: TestClient):
    funds = client.get("/funds").json()
    albion = next(f for f in funds if "Albion" in f["name"])

    response = client.get(f"/funds/{albion['id']}/portfolio")
    assert response.status_code == 200
    assert len(response.json()["companies"]) == 10


def test_fund_portfolio_404(client: TestClient):
    response = client.get("/funds/9999/portfolio")
    assert response.status_code == 404
