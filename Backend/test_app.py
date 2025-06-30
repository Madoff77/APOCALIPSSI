import os
from unittest.mock import patch
from app import app

os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
client = app.test_client()

EMAIL = "test@example.com"
PWD = "secret123"


def _register_and_token():
    client.post("/auth/register", json={"email": EMAIL, "password": PWD})
    resp = client.post("/auth/login", json={"email": EMAIL, "password": PWD})
    return resp.json["access_token"]


def test_register_and_login():
    token = _register_and_token()
    assert token


def test_summarize_requires_auth():
    resp = client.post("/summarize")
    assert resp.status_code == 401


@patch("summarizer.generate_summary", return_value={"summary": "fake", "important_points": []})
@patch("app.extract_text", return_value="dummy text")
def test_summarize_ok(mock_extract, mock_gen):
    token = _register_and_token()
    data = {
        "file": (open(__file__, "rb"), "dummy.pdf"),
    }
    resp = client.post(
        "/summarize",
        data=data,
        headers={"Authorization": f"Bearer {token}"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 201
    assert resp.json["summary"] == "fake"
