import os
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text


class BookType(BaseModel):
    id: int
    type: str


book_type_router = APIRouter(prefix="/book_type", tags=["book_type"])

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DB_URL)


@book_type_router.get("/")
def get_book_types() -> List[BookType]:
    query = "SELECT id, type FROM book_type ORDER BY type;"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        book_types = [dict(row._mapping) for row in result.fetchall()]
    return book_types


@book_type_router.get("/{book_type_id}")
def get_book_type(book_type_id: int) -> BookType:
    query = "SELECT id, type FROM book_type WHERE id = :book_type_id;"
    with engine.connect() as conn:
        result = conn.execute(text(query), {"book_type_id": book_type_id})
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {book_type_id}.",
        )
    return result.fetchone()._asdict()


@book_type_router.post("/")
def create_book_type(type: str) -> Dict[str, str]:
    query = "INSERT INTO book_type (type) VALUES (:type);"
    with engine.connect() as conn:
        conn.execute(text(query), {"type": type})
        conn.commit()
    return {"message": f"Type de livre '{type}' créé avec succès."}


@book_type_router.put("/{book_type_id}")
def update_book_type(book_type_id: int, type: str) -> Dict[str, str]:
    query = "UPDATE book_type SET type = :new_type WHERE id = :book_type_id;"
    with engine.connect() as conn:
        result = conn.execute(
            text(query), {"book_type_id": book_type_id, "new_type": type}
        )
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {book_type_id}.",
        )
    return {
        "message": f"Type de livre avec l'ID {book_type_id} mis à jour avec succès."
    }


@book_type_router.delete("/{book_type_id}")
def delete_book_type(book_type_id: int) -> Dict[str, str]:
    query = "DELETE FROM book_type WHERE id = :book_type_id;"
    with engine.connect() as conn:
        result = conn.execute(text(query), {"book_type_id": book_type_id})
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {book_type_id}.",
        )
    return {"message": f"Type de livre avec l'ID {book_type_id} supprimé avec succès."}
