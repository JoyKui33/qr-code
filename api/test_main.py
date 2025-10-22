from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_qr():
    url = "http://example.com"
    response = client.post("/generate-qr/", json={"url": url})

    assert response.status_code == 200
    assert "qr_code_url" in response.json()

def test_generate_qr_invalid_url():
    url = "invalid-url"
    response = client.post("/generate-qr/", json={"url": url})

    assert response.status_code == 422  # FastAPI validation error


def test_list_items():
    response = client.get("/items")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body  # ensure not empty
    assert {"id", "name", "description"} <= set(body[0].keys())
