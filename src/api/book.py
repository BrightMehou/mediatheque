from datetime import date
from typing import Dict, List

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from src.db.connection import engine


class BookBase(BaseModel):
    title: str
    author: int
    isbn: str
    publication_date: date
    type: str
    page_count: int


class Book(BookBase):
    id: int


book_router = APIRouter(prefix="/book", tags=["book"])


def validate_isbn(isbn: str) -> bool:
    cleaned = isbn.replace("-", "").replace(" ", "")
    if len(cleaned) == 10:
        if not cleaned[:9].isdigit() or not (
            cleaned[9].isdigit() or cleaned[9] in "Xx"
        ):
            return False

        total = 0
        for index, char in enumerate(cleaned):
            value = 10 - index
            if index == 9 and char in "Xx":
                total += 10
            else:
                total += int(char) * value
        return total % 11 == 0

    if len(cleaned) == 13 and cleaned.isdigit():
        total = 0
        for index, char in enumerate(cleaned):
            weight = 1 if index % 2 == 0 else 3
            total += int(char) * weight
        return total % 10 == 0

    return False


@book_router.get("/")
def load_books(
    types: List[str] = Query(default=None), author: str = None
) -> List[Dict]:

    query = """
    SELECT l.id, l.title, a.pseudonym AS author, l.publication_date, lt.type
    FROM book l
    JOIN author a ON l.author_id = a.id
    JOIN book_type lt ON l.type_id = lt.id
    WHERE 1=1
    """

    if types:
        type_list = ", ".join(f"'{t}'" for t in types)
        query += f" AND lt.type IN ({type_list})"

    if author:
        query += f" AND a.pseudonym ilike '%{author}%'"

    query += " LIMIT 100;"

    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)

    return df.to_dict(orient="records")


@book_router.post("/")
def create_book(book: BookBase) -> Dict[str, str]:
    type_query = "SELECT id FROM book_type WHERE type = :type;"
    insert_query = """
    INSERT INTO book (author_id, title, isbn, publication_date, type_id, page_count)
    VALUES (:author_id, :title, :isbn, :publication_date, :type_id, :page_count);
    """

    if not validate_isbn(book.isbn):
        raise HTTPException(
            status_code=422, detail="ISBN invalide ou format non supporté."
        )

    with engine.connect() as connection:
        type_result = connection.execute(text(type_query), {"type": book.type})
        type_row = type_result.fetchone()
        if type_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Type de livre '{book.type}' introuvable.",
            )
        connection.execute(
            text(insert_query),
            {
                "author_id": book.author,
                "title": book.title,
                "isbn": book.isbn,
                "publication_date": book.publication_date,
                "type_id": type_row._mapping["id"],
                "page_count": book.page_count,
            },
        )
        connection.commit()

    return {"message": f"Livre '{book.title}' créé avec succès."}


@book_router.put("/{book_id}")
def update_book(book_id: int, book: BookBase) -> Dict[str, str]:
    type_query = "SELECT id FROM book_type WHERE type = :type;"
    update_query = """
    UPDATE book
    SET author_id = :author_id,
        title = :title,
        isbn = :isbn,
        publication_date = :publication_date,
        type_id = :type_id,
        page_count = :page_count
    WHERE id = :book_id;
    """

    if not validate_isbn(book.isbn):
        raise HTTPException(
            status_code=422, detail="ISBN invalide ou format non supporté."
        )

    with engine.connect() as connection:
        type_result = connection.execute(text(type_query), {"type": book.type})
        type_row = type_result.fetchone()
        if type_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Type de livre '{book.type}' introuvable.",
            )

        result = connection.execute(
            text(update_query),
            {
                "author_id": book.author,
                "title": book.title,
                "isbn": book.isbn,
                "publication_date": book.publication_date,
                "type_id": type_row._mapping["id"],
                "page_count": book.page_count,
                "book_id": book_id,
            },
        )
        connection.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun livre trouvé avec l'ID {book_id}.",
        )

    return {"message": f"Livre avec l'ID {book_id} mis à jour avec succès."}
