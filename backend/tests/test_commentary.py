"""
Tests for the commentary endpoint.
- Without ANTHROPIC_API_KEY: must return available=False with a message
- Response structure must always conform to CommentaryResponse schema
"""

import os
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def _first_hanseatic_id(client: TestClient) -> int:
    funds = client.get("/funds").json()
    nordkap = next(f for f in funds if "Nordkap" in f["name"])
    companies = client.get(f"/funds/{nordkap['id']}/portfolio").json()["companies"]
    hanseatic = next(c for c in companies if "Hanseatic" in c["name"])
    return hanseatic["id"]


class TestCommentaryNoApiKey:
    def test_graceful_degrade_without_key(self, client: TestClient):
        """Without API key, response must be available=False, not 5xx."""
        company_id = _first_hanseatic_id(client)
        # Ensure ANTHROPIC_API_KEY is absent
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            # Reset module-level cached client
            import app.commentary as commentary_module
            commentary_module._CLIENT = None
            resp = client.post(f"/portfolio/{company_id}/commentary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is False
        assert "message" in data
        assert data["company_id"] == company_id

    def test_degrade_response_structure(self, client: TestClient):
        company_id = _first_hanseatic_id(client)
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            import app.commentary as commentary_module
            commentary_module._CLIENT = None
            resp = client.post(f"/portfolio/{company_id}/commentary")
        data = resp.json()
        assert "available" in data
        assert "sentences" in data
        assert isinstance(data["sentences"], list)

    def test_commentary_404_for_missing_company(self, client: TestClient):
        resp = client.post("/portfolio/99999/commentary")
        assert resp.status_code == 404


class TestCommentaryMocked:
    def test_mocked_claude_returns_sentences(self, client: TestClient):
        """With a mocked anthropic client, sentences and source_refs must be present."""
        company_id = _first_hanseatic_id(client)

        fake_response_text = (
            '[{"sentence": "Carbon intensity is elevated at 312 tCO2e/€M. [CARBON_INTENSITY_HIGH]", '
            '"source_refs": ["CARBON_INTENSITY_HIGH"]}, '
            '{"sentence": "Leverage at 6.9× EBITDA is above PE threshold. [LEVERAGE_HIGH]", '
            '"source_refs": ["LEVERAGE_HIGH"]}]'
        )
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=fake_response_text)]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_msg

        import app.commentary as commentary_module
        original_client = commentary_module._CLIENT
        commentary_module._CLIENT = mock_client
        try:
            resp = client.post(f"/portfolio/{company_id}/commentary")
        finally:
            commentary_module._CLIENT = original_client

        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True
        assert len(data["sentences"]) == 2
        for sentence in data["sentences"]:
            assert "sentence" in sentence
            assert "source_refs" in sentence
            assert isinstance(sentence["source_refs"], list)
