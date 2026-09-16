import pytest
from fastapi.testclient import TestClient
from app.core.fast_api_app import app

def test_health_endpoints():
    client = TestClient(app)
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}
    
    res_a2a = client.get("/api/a2a/v1/health")
    assert res_a2a.status_code == 200
    assert res_a2a.json() == {"status": "healthy"}

def test_a2a_gateway_routes_in_lifespan():
    with TestClient(app) as client:
        # 1. Verify Vertex AI gateway card path
        res_card = client.get("/api/a2a/v1/card")
        assert res_card.status_code == 200
        card_data = res_card.json()
        assert "name" in card_data
        assert "url" in card_data

        # 2. Verify fallback gateway card path
        res_card_fallback = client.get("/a2a/v1/card")
        assert res_card_fallback.status_code == 200
        assert res_card_fallback.json()["name"] == card_data["name"]

        # 3. Verify RPC routes exist (Method Not Allowed for GET on POST route, not 404)
        res_rpc = client.get("/api/a2a")
        assert res_rpc.status_code == 405
