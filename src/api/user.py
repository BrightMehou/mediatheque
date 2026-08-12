from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class UserBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    pseudonym: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserOut(UserBase):
    id: int


user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/", response_model=list[UserOut])
def get_users(connection: Annotated[Connection, Depends(get_db)]):
    query = "SELECT id, first_name, last_name, pseudonym, email FROM users ORDER BY last_name;"
    result = connection.execute(text(query))
    return result.mappings().all()


@user_router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, connection: Annotated[Connection, Depends(get_db)]):
    query = "SELECT id, first_name, last_name, pseudonym, email FROM users WHERE id = :user_id;"
    result = connection.execute(text(query), {"user_id": user_id})
    row = result.mappings().first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with ID {user_id}.",
        )
    return row


@user_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, int],
)
def create_user(user: UserCreate, connection: Annotated[Connection, Depends(get_db)]):
    query = """
    INSERT INTO users (first_name, last_name, pseudonym, email, password)
    VALUES (:first_name, :last_name, :pseudonym, :email, :password) RETURNING id;
    """
    result = connection.execute(text(query), user.model_dump())
    connection.commit()

    new_id = result.scalar()

    return {"id": new_id}


@user_router.put("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_user(
    user_id: int,
    user: UserUpdate,
    connection: Annotated[Connection, Depends(get_db)],
):
    query = """
    UPDATE users
    SET first_name = :first_name, last_name = :last_name, pseudonym = :pseudonym, email = :email
    WHERE id = :user_id;
    """
    result = connection.execute(
        text(query),
        {**user.model_dump(), "user_id": user_id},
    )
    connection.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with ID {user_id}.",
        )
