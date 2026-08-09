from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class BookBase(BaseModel):
    title: str
    author_id: int = Field(..., description="ID de l'auteur dans la base")
    isbn: str = Field(..., description="Numéro ISBN du livre")
    publication_date: date
    type: str
    page_count: int


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    publication_date: date
    type: str


book_router = APIRouter(prefix="/book", tags=["book"])


@book_router.get("/", response_model=list[BookOut])
def load_books(
    types: list[str] = Query(default=None),
    author: str | None = None,
    connection: Connection = Depends(get_db),
):
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

    query += " LIMIT 1000;"

    query_text = text(query)
    if "types" in bind_params:
        query_text = query_text.bindparams(bindparam("types", expanding=True))

    result = connection.execute(query_text, bind_params)
    return result.mappings().all()


@book_router.post("/", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, connection: Connection = Depends(get_db)):
    type_query = "SELECT id FROM book_type WHERE type = :type;"

    insert_query = """
    INSERT INTO book (
        author_id, title, isbn, publication_date, type_id, page_count
    )
    VALUES (
        :author_id, :title, :isbn, :publication_date, :type_id, :page_count
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
            "author_id": book.author_id,
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
    book_id: int, book: BookUpdate, connection: Connection = Depends(get_db)
):
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
            "author_id": book.author_id,
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
