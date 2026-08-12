from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class BookBase(BaseModel):
    title: str
    user_id: int = Field(..., description="ID de l'utilisateur dans la base")
    publication_date: date
    type: str


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookOut(BaseModel):
    id: int
    title: str
    pseudonym: str
    publication_date: date
    type: str


book_router = APIRouter(prefix="/book", tags=["book"])


@book_router.get("/", response_model=list[BookOut])
def load_books(
    connection: Annotated[Connection, Depends(get_db)],
    types: Annotated[list[str] | None, Query()] = None,
    user: str | None = None,
):
    query = """
    SELECT l.id, l.title, u.pseudonym AS pseudonym, l.publication_date, lt.type
    FROM book l
    JOIN users u ON l.user_id = u.id
    JOIN book_type lt ON l.type_id = lt.id
    WHERE 1=1
    """
    bind_params = {}

    if types:
        query += " AND lt.type IN :types"
        bind_params["types"] = tuple(types)

    if user:
        query += " AND a.pseudonym ILIKE :user"
        bind_params["user"] = f"%{user}%"

    query += " LIMIT 1000;"

    query_text = text(query)
    if "types" in bind_params:
        query_text = query_text.bindparams(bindparam("types", expanding=True))

    result = connection.execute(query_text, bind_params)
    return result.mappings().all()


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, int],
)
def create_book(book: BookCreate, connection: Annotated[Connection, Depends(get_db)]):
    type_query = "SELECT id FROM book_type WHERE type = :type;"

    insert_query = """
    INSERT INTO book (
        user_id, title, publication_date, type_id
    )
    VALUES (
        :user_id, :title, :publication_date, :type_id
    ) RETURNING id;
    """

    type_result = connection.execute(text(type_query), {"type": book.type})
    type_row = type_result.fetchone()

    if type_row is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid book type: '{book.type}' does not exist.",
        )

    result = connection.execute(
        text(insert_query),
        {
            "user_id": book.user_id,
            "title": book.title,
            "isbn": str(book.isbn),
            "publication_date": book.publication_date,
            "type_id": type_row._mapping["id"],
            "page_count": book.page_count,
        },
    )
    connection.commit()

    new_id = result.scalar()

    return {"id": new_id}


@book_router.put("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_book(
    book_id: int,
    book: BookUpdate,
    connection: Annotated[Connection, Depends(get_db)],
):
    type_query = "SELECT id FROM book_type WHERE type = :type;"

    update_query = """
    UPDATE book
    SET user_id = :user_id,
        title = :title,
        publication_date = :publication_date,
        type_id = :type_id,
    WHERE id = :book_id;
    """

    type_result = connection.execute(text(type_query), {"type": book.type})
    type_row = type_result.fetchone()

    if type_row is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid book type: '{book.type}' does not exist.",
        )

    result = connection.execute(
        text(update_query),
        {
            "user_id": book.user_id,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book found with ID {book_id}.",
        )
