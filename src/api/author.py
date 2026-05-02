from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from src.db.connection import engine


class AuthorBase(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    pseudonyme: str


class Author(AuthorBase):
    id: int


author_router = APIRouter(prefix="/author", tags=["author"])


@author_router.get("/")
def get_authors() -> List[Author]:
    query = "SELECT id, nom, prenom, pseudonyme FROM author ORDER BY nom;"
    with engine.connect() as connection:
        result = connection.execute(text(query))
        authors = [dict(row._mapping) for row in result.fetchall()]
    return authors


@author_router.get("/{author_id}")
def get_author(author_id: int) -> Author:
    query = "SELECT id, nom, prenom, pseudonyme FROM author WHERE id = :author_id;"
    with engine.connect() as connection:
        result = connection.execute(text(query), {"author_id": author_id})
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {author_id}."
        )
    return result.fetchone()._asdict()


@author_router.post("/")
def create_author(auteur: AuthorBase) -> Dict[str, str]:
    query = "INSERT INTO author (nom, prenom, pseudonyme) VALUES (:nom, :prenom, :pseudonyme);"
    with engine.connect() as connection:
        connection.execute(text(query), auteur.model_dump())
        connection.commit()
    return {"message": f"Auteur '{auteur.pseudonyme}' créé avec succès."}


@author_router.put("/{author_id}")
def update_author(author_id: int, auteur: AuthorBase) -> Dict[str, str]:
    query = "UPDATE author SET nom = :nom, prenom = :prenom, pseudonyme = :pseudonyme WHERE id = :author_id;"
    with engine.connect() as connection:
        result = connection.execute(
            text(query), {**auteur.model_dump(), "author_id": author_id}
        )
        connection.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {author_id}."
        )
    return {"message": f"Auteur avec l'ID {author_id} mis à jour avec succès."}
