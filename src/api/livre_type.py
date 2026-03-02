import os

from fastapi import APIRouter
from typing import Dict, List
from sqlalchemy import create_engine, text
import pandas as pd
from streamlit import connection

livre_type_router = APIRouter(prefix="/livre_types", tags=["livre_types"])

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DB_URL)


@livre_type_router.post("/")
def create_livre_type(type: str) -> Dict[str, str]:
    query = "INSERT INTO livre_type (type) VALUES (:type);"
    with engine.connect() as conn:
        conn.execute(text(query), {"type": type})
        conn.commit()
    return {"message": f"Type de livre '{type}' créé avec succès."}


@livre_type_router.get("/")
def load_types() -> List[str]:
    query = "SELECT type FROM livre_type ORDER BY type;"

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df["type"].tolist()

@livre_type_router.put("/{id}")
def update_livre_type(id: int, type: str) -> Dict[str, str]:
    query = "UPDATE livre_type SET type = :new_type WHERE id = :id;"
    with engine.connect() as conn:
        result = conn.execute(text(query), {"id": id, "new_type": type})
        conn.commit()
    if result.rowcount == 0:
        return {"message": f"Aucun type de livre trouvé avec l'ID {id}."}
    return {"message": f"Type de livre avec l'ID {id} mis à jour avec succès."}


@livre_type_router.delete("/{id}")
def delete_livre_type(id: int) -> Dict[str, str]:
    query = "DELETE FROM livre_type WHERE id = :id;"
    with engine.connect() as conn:
        result = conn.execute(text(query), {"id": id})
        conn.commit()
    if result.rowcount == 0:
        return {"message": f"Aucun type de livre trouvé avec l'ID {id}."}
    return {"message": f"Type de livre avec l'ID {id} supprimé avec succès."}
