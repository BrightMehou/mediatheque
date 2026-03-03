import os
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text

livre_type_router = APIRouter(prefix="/livre_type", tags=["livre_type"])

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DB_URL)


@livre_type_router.get("/")
def get_livre_types() -> List[Dict]:
    query = "SELECT id, type FROM livre_type ORDER BY type;"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        livre_types = [dict(row._mapping) for row in result.fetchall()]
    return livre_types


@livre_type_router.get("/{livre_type_id}")
def get_livre_type(livre_type_id: int) -> Dict:
    query = "SELECT id, type FROM livre_type WHERE id = :livre_type_id;"
    with engine.connect() as conn:
        result = conn.execute(text(query), {"livre_type_id": livre_type_id})
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {livre_type_id}.",
        )
    return result.fetchone()._asdict()


@livre_type_router.post("/")
def create_livre_type(type: str) -> Dict[str, str]:
    query = "INSERT INTO livre_type (type) VALUES (:type);"
    with engine.connect() as conn:
        conn.execute(text(query), {"type": type})
        conn.commit()
    return {"message": f"Type de livre '{type}' créé avec succès."}


@livre_type_router.put("/{livre_type_id}")
def update_livre_type(livre_type_id: int, type: str) -> Dict[str, str]:
    query = "UPDATE livre_type SET type = :new_type WHERE id = :livre_type_id;"
    with engine.connect() as conn:
        result = conn.execute(
            text(query), {"livre_type_id": livre_type_id, "new_type": type}
        )
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {livre_type_id}.",
        )
    return {
        "message": f"Type de livre avec l'ID {livre_type_id} mis à jour avec succès."
    }


@livre_type_router.delete("/{livre_type_id}")
def delete_livre_type(livre_type_id: int) -> Dict[str, str]:
    query = "DELETE FROM livre_type WHERE id = :livre_type_id;"
    with engine.connect() as conn:
        result = conn.execute(text(query), {"livre_type_id": livre_type_id})
        conn.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun type de livre trouvé avec l'ID {livre_type_id}.",
        )
    return {"message": f"Type de livre avec l'ID {livre_type_id} supprimé avec succès."}
