"""Fallback + structure tests for the AI risk interpretation and ingestion endpoints."""

from unittest.mock import patch
from fastapi.testclient import TestClient


def _a_company_id(client: TestClient) -> int:
    funds = client.get("/funds").json()
    fid = funds[0]["id"]
    return client.get(f"/funds/{fid}/portfolio").json()["companies"][0]["id"]


def test_interpretation_degrades_without_key(client: TestClient):
    cid = _a_company_id(client)
    with patch("app.ai_gateway.is_configured", return_value=False):
        resp = client.post(f"/portfolio/{cid}/interpretation")
    assert resp.status_code == 200
    data = resp.json()
    assert data["available"] is False
    assert data["key_risks"] == []


def test_interpretation_mocked(client: TestClient):
    cid = _a_company_id(client)
    fake = {"thesis": "Forward-looking pressure from carbon and leverage.",
            "key_risks": [{"title": "Carbon transition", "severity": "high",
                           "rationale": "High intensity vs EU ETS anchor.",
                           "source_refs": ["CARBON_INTENSITY_HIGH"]}]}
    with patch("app.ai_gateway.is_configured", return_value=True), \
         patch("app.ai_gateway.chat_json", return_value=fake):
        resp = client.post(f"/portfolio/{cid}/interpretation")
    data = resp.json()
    assert data["available"] is True
    assert data["thesis"].startswith("Forward")
    assert data["key_risks"][0]["severity"] == "high"


def test_normalize_degrades_without_key(client: TestClient):
    with patch("app.ai_gateway.is_configured", return_value=False):
        resp = client.post("/ingestion/normalize", json={"rows": [{"Umsatz": 1000}]})
    assert resp.status_code == 200
    assert resp.json()["available"] is False


def test_normalize_mocked(client: TestClient):
    fake = {"rows": [{"year": 2023, "quarter": 4, "revenue": 1000000.0,
                      "ebitda": 200000.0, "net_debt": 500000.0}],
            "field_mapping": {"Umsatz": "revenue", "Jahr": "year"},
            "notes": "Amounts assumed in absolute EUR."}
    with patch("app.ai_gateway.is_configured", return_value=True), \
         patch("app.ai_gateway.chat_json", return_value=fake):
        resp = client.post("/ingestion/normalize",
                           json={"rows": [{"Umsatz": 1000000, "Jahr": 2023, "Q": 4}], "source_hint": "SAP"})
    data = resp.json()
    assert data["available"] is True
    assert data["rows"][0]["revenue"] == 1000000.0
    assert data["field_mapping"]["Umsatz"] == "revenue"
