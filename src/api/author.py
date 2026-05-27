from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from src.db.connection import engine


class AuthorBase(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    pseudonym: str


class Author(AuthorBase):
    id: int


author_router = APIRouter(prefix="/author", tags=["author"])


@author_router.get("/")
def get_authors() -> List[Author]:
    query = (
        "SELECT id, last_name, first_name, pseudonym FROM author ORDER BY last_name;"
    )
    with engine.connect() as connection:
        result = connection.execute(text(query))
        authors = [dict(row._mapping) for row in result.fetchall()]
    return authors


@author_router.get("/{author_id}")
def get_author(author_id: int) -> Author:
    query = (
        "SELECT id, last_name, first_name, pseudonym FROM author WHERE id = :author_id;"
    )
    with engine.connect() as connection:
        result = connection.execute(text(query), {"author_id": author_id})
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {author_id}."
        )
    return result.fetchone()._asdict()


@author_router.post("/")
def create_author(author: AuthorBase) -> Dict[str, str]:
    query = "INSERT INTO author (last_name, first_name, pseudonym) VALUES (:last_name, :first_name, :pseudonym);"
    with engine.connect() as connection:
        connection.execute(text(query), author.model_dump())
        connection.commit()
    return {"message": f"Auteur '{author.pseudonym}' créé avec succès."}


@author_router.put("/{author_id}")
def update_author(author_id: int, author: AuthorBase) -> Dict[str, str]:
    query = "UPDATE author SET last_name = :last_name, first_name = :first_name, pseudonym = :pseudonym WHERE id = :author_id;"
    with engine.connect() as connection:
        result = connection.execute(
            text(query), {**author.model_dump(), "author_id": author_id}
        )
        connection.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {author_id}."
        )
    return {"message": f"Auteur avec l'ID {author_id} mis à jour avec succès."}
