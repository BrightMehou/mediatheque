from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class BookTypeBase(BaseModel):
    type: str


class BookTypeCreate(BookTypeBase):
    pass


class BookTypeUpdate(BookTypeBase):
    pass


class BookTypeOut(BookTypeBase):
    id: int


book_type_router = APIRouter(prefix="/book_type", tags=["book_type"])


@book_type_router.get("/", response_model=List[BookTypeOut])
def get_book_types(connection: Connection = Depends(get_db)):
    query = "SELECT id, type FROM book_type ORDER BY type;"
    result = connection.execute(text(query))
    return result.mappings().all()


@book_type_router.post("/", status_code=status.HTTP_201_CREATED)
def create_book_type(
    book_type: BookTypeCreate, connection: Connection = Depends(get_db)
):
    query = "INSERT INTO book_type (type) VALUES (:type) RETURNING id;"
    result = connection.execute(text(query), {"type": book_type.type})
    connection.commit()

    new_id = result.scalar()

    return {"id": new_id}


@book_type_router.put("/{book_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_book_type(
    book_type_id: int,
    book_type: BookTypeUpdate,
    connection: Connection = Depends(get_db),
):
    query = "UPDATE book_type SET type = :new_type WHERE id = :book_type_id;"
    result = connection.execute(
        text(query), {"book_type_id": book_type_id, "new_type": book_type.type}
    )
    connection.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {book_type_id}.",
        )


@book_type_router.delete("/{book_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_type(book_type_id: int, connection: Connection = Depends(get_db)):
    query = "DELETE FROM book_type WHERE id = :book_type_id;"
    result = connection.execute(text(query), {"book_type_id": book_type_id})
    connection.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {book_type_id}.",
        )
