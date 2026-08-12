from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "API de la médiathèque opérationnelle."}


def test_health_check_success(client: TestClient, mock_db_conn: MagicMock) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}
    mock_db_conn.execute.assert_called_once()


def test_health_check_db_failure(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_db_conn.execute.side_effect = Exception("Erreur simulée")
    mock_logger_error = mocker.patch("src.api.main.logger.error")

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Service indisponible (Erreur de base de données).",
    }
    mock_logger_error.assert_called_once()
