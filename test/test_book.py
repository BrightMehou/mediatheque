from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


def test_load_books_no_filters(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.mappings().all.return_value = [
        {
            "id": 1,
            "title": "Dune",
            "author": "Frank Herbert",
            "publication_date": "1965-08-01",
            "type": "Science-Fiction",
        },
    ]
    mock_db_conn.execute.return_value = mock_result

    response = client.get("/book/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "Dune",
            "author": "Frank Herbert",
            "publication_date": "1965-08-01",
            "type": "Science-Fiction",
        },
    ]
    mock_db_conn.execute.assert_called_once()


def test_load_books_with_filters(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_result = mocker.MagicMock()
    mock_result.mappings().all.return_value = []
    mock_db_conn.execute.return_value = mock_result

    # On passe des paramètres de requête (query params)
    response = client.get("/book/?types=Roman&types=Poésie&author=Hugo")

    assert response.status_code == 200
    assert response.json() == []
    mock_db_conn.execute.assert_called_once()


def test_create_book_success(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_type_result = mocker.MagicMock()
    type_row = mocker.MagicMock()
    type_row._mapping = {"id": 2}
    mock_type_result.fetchone.return_value = type_row

    mock_insert_result = mocker.MagicMock()
    mock_insert_result.scalar.return_value = 42

    mock_db_conn.execute.side_effect = [mock_type_result, mock_insert_result]

    payload = {
        "title": "Les Misérables",
        "author_id": 1,
        "isbn": "978-2-253-09633-7",
        "publication_date": "1862-04-03",
        "type": "Roman",
        "page_count": 1500,
    }

    response = client.post("/book/", json=payload)

    assert response.status_code == 201
    assert response.json() == {"id": 42}
    assert mock_db_conn.execute.call_count == 2
    mock_db_conn.commit.assert_called_once()


def test_create_book_type_not_found(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_type_result = mocker.MagicMock()
    mock_type_result.fetchone.return_value = None
    mock_db_conn.execute.return_value = mock_type_result

    payload = {
        "title": "Les Misérables",
        "author_id": 1,
        "isbn": "978-2-253-09633-7",
        "publication_date": "1862-04-03",
        "type": "TypeInconnu",
        "page_count": 1500,
    }

    response = client.post("/book/", json=payload)

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Invalid book type: 'TypeInconnu' does not exist.",
    }
    mock_db_conn.execute.assert_called_once()  # On s'arrête au SELECT
    mock_db_conn.commit.assert_not_called()


def test_update_book_success(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_type_result = mocker.MagicMock()
    type_row = mocker.MagicMock()
    type_row._mapping = {"id": 2}
    mock_type_result.fetchone.return_value = type_row

    mock_update_result = mocker.MagicMock()
    mock_update_result.rowcount = 1

    mock_db_conn.execute.side_effect = [mock_type_result, mock_update_result]

    payload = {
        "title": "Les Misérables - Édition révisée",
        "author_id": 1,
        "isbn": "978-2-253-09633-7",
        "publication_date": "1862-04-03",
        "type": "Roman",
        "page_count": 1550,
    }

    response = client.put("/book/1", json=payload)

    assert response.status_code == 204
    assert mock_db_conn.execute.call_count == 2
    mock_db_conn.commit.assert_called_once()


def test_update_book_not_found(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_type_result = mocker.MagicMock()
    type_row = mocker.MagicMock()
    type_row._mapping = {"id": 2}
    mock_type_result.fetchone.return_value = type_row

    mock_update_result = mocker.MagicMock()
    mock_update_result.rowcount = 0

    mock_db_conn.execute.side_effect = [mock_type_result, mock_update_result]

    payload = {
        "title": "Livre inexistant",
        "author_id": 1,
        "isbn": "978-2-253-09633-7",
        "publication_date": "2024-01-01",
        "type": "Roman",
        "page_count": 300,
    }

    response = client.put("/book/999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "No book found with ID 999."}
    assert mock_db_conn.execute.call_count == 2


def test_update_book_type_not_found(
    client: TestClient, mock_db_conn: MagicMock, mocker: MockerFixture
) -> None:
    mock_type_result = mocker.MagicMock()
    mock_type_result.fetchone.return_value = None
    mock_db_conn.execute.return_value = mock_type_result

    payload = {
        "title": "Livre",
        "author_id": 1,
        "isbn": "978-2-253-09633-7",
        "publication_date": "2024-01-01",
        "type": "Bizarre",
        "page_count": 300,
    }

    response = client.put("/book/1", json=payload)

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid book type: 'Bizarre' does not exist."}
    mock_db_conn.execute.assert_called_once()
    mock_db_conn.commit.assert_not_called()
