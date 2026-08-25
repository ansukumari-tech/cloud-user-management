import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["INTERNAL_SERVICE_KEY"] = "test-internal-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from models import db  # noqa: E402


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.create_all()
    with flask_app.test_client() as client:
        yield client
    with flask_app.app_context():
        db.drop_all()


def test_register_creates_user(client):
    response = client.post("/register", json={"username": "alice", "password": "pass1234"})
    assert response.status_code == 201


def test_register_rejects_duplicate(client):
    client.post("/register", json={"username": "bob", "password": "pass1234"})
    response = client.post("/register", json={"username": "bob", "password": "pass1234"})
    assert response.status_code == 400


def test_login_returns_token(client):
    client.post("/register", json={"username": "carol", "password": "pass1234"})
    response = client.post("/login", json={"username": "carol", "password": "pass1234"})
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_login_rejects_wrong_password(client):
    client.post("/register", json={"username": "dave", "password": "pass1234"})
    response = client.post("/login", json={"username": "dave", "password": "wrong"})
    assert response.status_code == 401


def test_internal_endpoint_requires_key(client):
    response = client.get("/internal/users")
    assert response.status_code == 403


def test_internal_endpoint_works_with_key(client):
    client.post("/register", json={"username": "erin", "password": "pass1234"})
    response = client.get("/internal/users", headers={"X-Internal-Key": "test-internal-key"})
    assert response.status_code == 200
    assert len(response.get_json()) == 1
