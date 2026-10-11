from fastapi.testclient import TestClient
from app.main import app

clinet = TestClient(app)

def test_health():
    response = clinet.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "CM Enterprise IncidentOps API"
    }