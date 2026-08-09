import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.connection import get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db_conn(mocker):
    mock_conn = mocker.MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_conn
    yield mock_conn
    app.dependency_overrides.clear()
