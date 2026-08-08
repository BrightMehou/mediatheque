from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class AuthorBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    pseudonym: str


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(AuthorBase):
    pass


class AuthorOut(AuthorBase):
    id: int


author_router = APIRouter(prefix="/author", tags=["author"])


@author_router.get("/", response_model=List[AuthorOut])
def get_authors(connection: Connection = Depends(get_db)):
    query = (
        "SELECT id, first_name, last_name, pseudonym FROM author ORDER BY last_name;"
    )
    result = connection.execute(text(query))
    return result.mappings().all()


@author_router.get("/{author_id}", response_model=AuthorOut)
def get_author(author_id: int, connection: Connection = Depends(get_db)):
    query = (
        "SELECT id, first_name, last_name, pseudonym FROM author WHERE id = :author_id;"
    )
    result = connection.execute(text(query), {"author_id": author_id})
    row = result.mappings().first()

    if row is None:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {author_id}."
        )
    return row


@author_router.post("/", status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, connection: Connection = Depends(get_db)):
    query = """
    INSERT INTO author (first_name, last_name, pseudonym) 
    VALUES (:first_name, :last_name, :pseudonym) RETURNING id;
    """
    result = connection.execute(text(query), author.model_dump())
    connection.commit()

    new_id = result.scalar()

    return {"id": new_id}


@author_router.put("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_author(
    author_id: int, author: AuthorUpdate, connection: Connection = Depends(get_db)
):
    query = """
    UPDATE author 
    SET first_name = :first_name, last_name = :last_name, pseudonym = :pseudonym 
    WHERE id = :author_id;
    """
    result = connection.execute(
        text(query), {**author.model_dump(), "author_id": author_id}
    )
    connection.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, detail=f"Aucun auteur trouvé avec l'ID {author_id}."
        )
