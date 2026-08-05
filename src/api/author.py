from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class AuthorBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    pseudonym: str


class Author(AuthorBase):
    id: int


author_router = APIRouter(prefix="/author", tags=["author"])


@author_router.get("/")
def get_authors(connection: Connection = Depends(get_db)) -> List[Author]:
    query = (
        "SELECT id, first_name, last_name, pseudonym FROM author ORDER BY last_name;"
    )
    result = connection.execute(text(query))
    authors = [dict(row._mapping) for row in result.fetchall()]
    return authors


@author_router.get("/{author_id}")
def get_author(author_id: int, connection: Connection = Depends(get_db)) -> Author:
    query = (
        "SELECT id, first_name, last_name, pseudonym FROM author WHERE id = :author_id;"
    )
    result = connection.execute(text(query), {"author_id": author_id})
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {author_id}."
        )
    return result.fetchone()._asdict()


@author_router.post("/")
def create_author(
    author: AuthorBase, connection: Connection = Depends(get_db)
) -> Dict[str, str]:
    query = "INSERT INTO author (first_name, last_name, pseudonym) VALUES (:first_name, :last_name, :pseudonym);"
    connection.execute(text(query), author.model_dump())
    connection.commit()
    return {"message": f"Auteur '{author.pseudonym}' créé avec succès."}


@author_router.put("/{author_id}")
def update_author(
    author_id: int, author: AuthorBase, connection: Connection = Depends(get_db)
) -> Dict[str, str]:
    query = "UPDATE author SET first_name = :first_name, last_name = :last_name, pseudonym = :pseudonym WHERE id = :author_id;"
    result = connection.execute(
        text(query), {**author.model_dump(), "author_id": author_id}
    )
    connection.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {author_id}."
        )
    return {"message": f"Auteur avec l'ID {author_id} mis à jour avec succès."}
