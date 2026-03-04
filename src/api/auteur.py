import os
from typing import List, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text


class AuteurBase(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    pseudonyme: str


class Auteur(AuteurBase):
    id: int


auteur_router = APIRouter(prefix="/auteur", tags=["auteur"])

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DB_URL)


@auteur_router.get("/")
def get_auteurs() -> List[Auteur]:
    query = "SELECT id, nom, prenom, pseudonyme FROM auteur ORDER BY nom;"
    with engine.connect() as connection:
        result = connection.execute(text(query))
        auteurs = [dict(row._mapping) for row in result.fetchall()]
    return auteurs


@auteur_router.get("/{auteur_id}")
def get_auteur(auteur_id: int) -> Auteur:
    query = "SELECT id, nom, prenom, pseudonyme FROM auteur WHERE id = :auteur_id;"
    with engine.connect() as connection:
        result = connection.execute(text(query), {"auteur_id": auteur_id})
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {auteur_id}."
        )
    return result.fetchone()._asdict()

@auteur_router.post("/")
def create_auteur(auteur: AuteurBase) -> Dict[str, str]:
    query = "INSERT INTO auteur (nom, prenom, pseudonyme) VALUES (:nom, :prenom, :pseudonyme);"
    with engine.connect() as connection:
        connection.execute(
            text(query), auteur.model_dump()
        )
        connection.commit()
    return {"message": f"Auteur '{auteur.pseudonyme}' créé avec succès."}

@auteur_router.put("/{auteur_id}")
def update_auteur(auteur_id: int, auteur: AuteurBase) -> Dict[str, str]:
    query = "UPDATE auteur SET nom = :nom, prenom = :prenom, pseudonyme = :pseudonyme WHERE id = :auteur_id;"
    with engine.connect() as connection:
        result = connection.execute(
            text(query), {**auteur.model_dump(), "auteur_id": auteur_id}
        )
        connection.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {auteur_id}."
        )
    return {"message": f"Auteur avec l'ID {auteur_id} mis à jour avec succès."}
