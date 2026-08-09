from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


def test_get_authors(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.mappings().all.return_value = [
        {"id": 1, "first_name": "Victor", "last_name": "Hugo", "pseudonym": "VH"},
        {"id": 2, "first_name": None, "last_name": None, "pseudonym": "Molière"},
    ]
    mock_db_conn.execute.return_value = mock_result

    response = client.get("/author/")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "first_name": "Victor", "last_name": "Hugo", "pseudonym": "VH"},
        {"id": 2, "first_name": None, "last_name": None, "pseudonym": "Molière"},
    ]
    mock_db_conn.execute.assert_called_once()


def test_get_author_success(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.mappings().first.return_value = {
        "id": 1,
        "first_name": "Victor",
        "last_name": "Hugo",
        "pseudonym": "VH",
    }
    mock_db_conn.execute.return_value = mock_result

    response = client.get("/author/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "first_name": "Victor",
        "last_name": "Hugo",
        "pseudonym": "VH",
    }
    mock_db_conn.execute.assert_called_once()


def test_get_author_not_found(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.mappings().first.return_value = None
    mock_db_conn.execute.return_value = mock_result

    response = client.get("/author/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "No author found with ID 999."}
    mock_db_conn.execute.assert_called_once()


def test_create_author(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.scalar.return_value = 5
    mock_db_conn.execute.return_value = mock_result

    payload = {"first_name": "Émile", "last_name": "Zola", "pseudonym": "Zola"}
    response = client.post("/author/", json=payload)

    assert response.status_code == 201
    assert response.json() == {"id": 5}
    mock_db_conn.execute.assert_called_once()
    mock_db_conn.commit.assert_called_once()


def test_update_author_success(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.rowcount = 1
    mock_db_conn.execute.return_value = mock_result

    payload = {"first_name": "George", "last_name": "Sand", "pseudonym": "Amantine"}
    response = client.put("/author/1", json=payload)

    assert response.status_code == 204
    mock_db_conn.execute.assert_called_once()
    mock_db_conn.commit.assert_called_once()


def test_update_author_not_found(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.rowcount = 0
    mock_db_conn.execute.return_value = mock_result

    payload = {"first_name": "George", "last_name": "Sand", "pseudonym": "Amantine"}
    response = client.put("/author/999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "No author found with ID 999."}
    mock_db_conn.execute.assert_called_once()
