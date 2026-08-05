from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class BookType(BaseModel):
    id: int
    type: str


book_type_router = APIRouter(prefix="/book_type", tags=["book_type"])


@book_type_router.get("/")
def get_book_types(connection: Connection = Depends(get_db)) -> List[BookType]:
    query = "SELECT id, type FROM book_type ORDER BY type;"
    result = connection.execute(text(query))
    book_types = [dict(row._mapping) for row in result.fetchall()]
    return book_types


@book_type_router.post("/")
def create_book_type(
    type: str, connection: Connection = Depends(get_db)
) -> Dict[str, str]:
    query = "INSERT INTO book_type (type) VALUES (:type);"
    connection.execute(text(query), {"type": type})
    connection.commit()
    return {"message": f"Type de livre '{type}' créé avec succès."}


@book_type_router.put("/{book_type_id}")
def update_book_type(
    book_type_id: int, type: str, connection: Connection = Depends(get_db)
) -> Dict[str, str]:
    query = "UPDATE book_type SET type = :new_type WHERE id = :book_type_id;"
    result = connection.execute(
        text(query), {"book_type_id": book_type_id, "new_type": type}
    )
    connection.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {book_type_id}.",
        )
    return {
        "message": f"Type de livre avec l'ID {book_type_id} mis à jour avec succès."
    }


@book_type_router.delete("/{book_type_id}")
def delete_book_type(
    book_type_id: int, connection: Connection = Depends(get_db)
) -> Dict[str, str]:
    query = "DELETE FROM book_type WHERE id = :book_type_id;"
    result = connection.execute(text(query), {"book_type_id": book_type_id})
    connection.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {book_type_id}.",
        )
    return {"message": f"Type de livre avec l'ID {book_type_id} supprimé avec succès."}
