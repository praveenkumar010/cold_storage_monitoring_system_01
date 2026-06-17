from fastapi.testclient import TestClient
from app.main import app
from .conftest import client

client = TestClient(app)

def test_login_page():
    response = client.get("/login")

    assert response.status_code == 200