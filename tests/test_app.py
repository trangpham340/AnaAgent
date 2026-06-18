from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_returns_public_api_links() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Analysis Agent AI" in response.text
    assert "/docs" in response.text
    assert "/health" in response.text
    assert "/api/v1/analyze" in response.text


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_without_api_key_uses_fallback() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={
            "project_name": "Demo",
            "content": "Build an internal AI assistant for project analysis and task planning.",
            "goals": ["Find delivery risks"],
            "constraints": ["Small team"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["project_name"] == "Demo"
    assert body["source"] in {"local", "openai"}
    assert body["findings"]
