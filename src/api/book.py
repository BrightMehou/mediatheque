from datetime import date
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic_extra_types.isbn import ISBN
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class BookBase(BaseModel):
    title: str
    author: int
    isbn: ISBN
    publication_date: date
    type: str
    page_count: int


class Book(BookBase):
    id: int


book_router = APIRouter(prefix="/book", tags=["book"])


@book_router.get("/")
def load_books(
    types: List[str] = Query(default=None),
    author: str = None,
    connection: Connection = Depends(get_db),
) -> List[Dict]:

    query = """
    SELECT l.id, l.title, a.pseudonym AS author, l.publication_date, lt.type
    FROM book l
    JOIN author a ON l.author_id = a.id
    JOIN book_type lt ON l.type_id = lt.id
    WHERE 1=1
    """

    bind_params = {}

    if types:
        query += " AND lt.type IN :types"
        bind_params["types"] = tuple(types)

    if author:
        query += " AND a.pseudonym ILIKE :author"
        bind_params["author"] = f"%{author}%"

    query += " LIMIT 100;"

    query_text = text(query)
    if "types" in bind_params:
        query_text = query_text.bindparams(bindparam("types", expanding=True))

    result = connection.execute(query_text, bind_params)
    return [dict(row._mapping) for row in result]


@book_router.post("/")
def create_book(
    book: BookBase, connection: Connection = Depends(get_db)
) -> Dict[str, str]:
    type_query = "SELECT id FROM book_type WHERE type = :type;"

    insert_query = """
    INSERT INTO book (
        author_id,
        title,
        isbn,
        publication_date,
        type_id,
        page_count
    )
    VALUES (
        :author_id,
        :title,
        :isbn,
        :publication_date,
        :type_id,
        :page_count
    );
    """

    type_result = connection.execute(
        text(type_query),
        {"type": book.type},
    )

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
            "isbn": str(book.isbn),
            "publication_date": book.publication_date,
            "type_id": type_row._mapping["id"],
            "page_count": book.page_count,
        },
    )

    connection.commit()

    return {"message": f"Livre '{book.title}' créé avec succès."}


@book_router.put("/{book_id}")
def update_book(
    book_id: int, book: BookBase, connection: Connection = Depends(get_db)
) -> Dict[str, str]:
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

    type_result = connection.execute(
        text(type_query),
        {"type": book.type},
    )

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
            "isbn": str(book.isbn),
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
