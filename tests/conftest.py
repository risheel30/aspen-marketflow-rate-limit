import pytest
from fastapi.testclient import TestClient
from marketflow.main import app
from marketflow.models import reset_db


@pytest.fixture(autouse=True)
def run_around_tests():
    reset_db()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_sandbox():
    return {"X-User-Id": "usr-sandbox-99"}


@pytest.fixture
def auth_production():
    return {"X-User-Id": "usr-prod-10"}


@pytest.fixture
def auth_production_secondary():
    return {"X-User-Id": "usr-prod-20"}
