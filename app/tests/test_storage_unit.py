from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_storage_unit_route_exists():

    response = client.post(
    "/ui/storage-units/create",
    data={
        "warehouse_id": 1,
        "name": "Unit Test",
        "unit_type": "Cold Room"
    },
    follow_redirects=False
)

    assert response.status_code in [302, 303]