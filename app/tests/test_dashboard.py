from .conftest import client

def test_dashboard_redirect():
    response = client.get(
        "/dashboard",
        follow_redirects=False
    )

    assert response.status_code in [302, 303]