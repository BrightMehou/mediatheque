from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


def test_get_book_types(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.mappings().all.return_value = [
        {"type": "Roman", "id": 1},
        {"type": "Science-Fiction", "id": 2},
    ]
    mock_db_conn.execute.return_value = mock_result

    response = client.get("/book_type/")

    assert response.status_code == 200
    assert response.json() == [
        {"type": "Roman", "id": 1},
        {"type": "Science-Fiction", "id": 2},
    ]
    mock_db_conn.execute.assert_called_once()


def test_create_book_type(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.scalar.return_value = 10
    mock_db_conn.execute.return_value = mock_result

    response = client.post("/book_type/", json={"type": "Policier"})

    assert response.status_code == 201
    assert response.json() == {"id": 10}
    mock_db_conn.execute.assert_called_once()
    mock_db_conn.commit.assert_called_once()


def test_update_book_type_success(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.rowcount = 1
    mock_db_conn.execute.return_value = mock_result

    response = client.put("/book_type/1", json={"type": "Roman Historique"})

    assert response.status_code == 204
    mock_db_conn.commit.assert_called_once()


def test_update_book_type_not_found(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.rowcount = 0
    mock_db_conn.execute.return_value = mock_result

    response = client.put("/book_type/999", json={"type": "Inexistant"})

    assert response.status_code == 404
    assert response.json() == {"detail": "No book type found with ID 999."}


def test_delete_book_type_success(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.rowcount = 1
    mock_db_conn.execute.return_value = mock_result

    response = client.delete("/book_type/1")

    assert response.status_code == 204
    mock_db_conn.commit.assert_called_once()


def test_delete_book_type_not_found(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.rowcount = 0
    mock_db_conn.execute.return_value = mock_result

    response = client.delete("/book_type/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "No book type found with ID 999."}
