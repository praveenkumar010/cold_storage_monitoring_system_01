from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_alert_route():

    response = client.get(
        "/dashboard"
    )

    assert response.status_code in [200,302,303]