from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.api.main import app
from src.db.connection import get_db


@pytest.fixture
def client() -> Generator[TestClient]:
    """Fixture fournissant un client de test pour FastAPI."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db_conn(mocker: MockerFixture) -> Generator[MagicMock]:
    """Surcharge la dépendance de la base de données avec un mock."""
    mock_conn = mocker.MagicMock()

    app.dependency_overrides[get_db] = lambda: mock_conn

    yield mock_conn

    app.dependency_overrides.clear()


# @pytest.fixture(autouse=True)
# def clean_database():
#     """Nettoie la table topic avant chaque test."""
#     db = get_db()
#     connection = next(db)

#     connection.execute(
#         text(
#             """
#             TRUNCATE TABLE topic RESTART IDENTITY CASCADE;
#             """
#         )
#     )
#     connection.commit()

#     yield
