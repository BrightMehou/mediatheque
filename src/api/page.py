from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class pageBase(BaseModel):
    title: str
    user_id: int = Field(..., description="ID de l'utilisateur dans la base")
    publication_date: date
    topic: str


class pageCreate(pageBase):
    pass


class pageUpdate(pageBase):
    pass


class pageOut(BaseModel):
    id: int
    title: str
    pseudo: str
    publication_date: date
    topic: str


def check_topic_exists(connection: Connection, topic_name: str) -> bool:
    query = "SELECT id FROM topic WHERE topic = :topic;"
    result = connection.execute(text(query), {"topic": topic_name})
    return result.fetchone()


def check_author_exists(connection: Connection, user_id: int) -> bool:
    query = "SELECT id FROM users WHERE id = :user_id;"
    result = connection.execute(text(query), {"user_id": user_id})
    return result.fetchone()


page_router = APIRouter(prefix="/page", tags=["page"])


@page_router.get("/", response_model=list[pageOut])
def load_pages(
    connection: Annotated[Connection, Depends(get_db)],
    topics: Annotated[list[str] | None, Query()] = None,
    user: str | None = None,
):
    query = """
    SELECT p.id, p.title, u.pseudo AS pseudo, p.publication_date, lt.topic
    FROM page p
    JOIN users u ON p.user_id = u.id
    JOIN topic lt ON p.topic_id = lt.id
    WHERE 1=1
    """
    bind_params = {}

    if topics:
        query += " AND lt.topic IN :topics"
        bind_params["topics"] = tuple(topics)

    if user:
        query += " AND u.pseudo ILIKE :user"
        bind_params["user"] = f"%{user}%"

    query += " LIMIT 1000;"

    query_text = text(query)
    if "topics" in bind_params:
        query_text = query_text.bindparams(bindparam("topics", expanding=True))

    result = connection.execute(query_text, bind_params)
    return result.mappings().all()


@page_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, int],
)
def create_page(page: pageCreate, connection: Annotated[Connection, Depends(get_db)]):

    insert_query = """
    INSERT INTO page (
        user_id, title, publication_date, topic_id
    )
    VALUES (
        :user_id, :title, :publication_date, :topic_id
    ) RETURNING id;
    """

    topic_row = check_topic_exists(connection, page.topic)

    if topic_row is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid topic: '{page.topic}' does not exist.",
        )

    author_row = check_author_exists(connection, page.user_id)
    if author_row is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid author: '{page.user_id}' does not exist.",
        )

    result = connection.execute(
        text(insert_query),
        {
            "user_id": page.user_id,
            "title": page.title,
            "publication_date": page.publication_date,
            "topic_id": topic_row._mapping["id"],
        },
    )
    connection.commit()

    new_id = result.scalar()

    return {"id": new_id}


@page_router.put("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_page(
    page_id: int,
    page: pageUpdate,
    connection: Annotated[Connection, Depends(get_db)],
):

    update_query = """
    UPDATE page
    SET user_id = :user_id,
        title = :title,
        publication_date = :publication_date,
        topic_id = :topic_id
    WHERE id = :page_id;
    """

    topic_row = check_topic_exists(connection, page.topic)

    if topic_row is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid topic: '{page.topic}' does not exist.",
        )

    author_row = check_author_exists(connection, page.user_id)

    if author_row is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid author: '{page.user_id}' does not exist.",
        )

    result = connection.execute(
        text(update_query),
        {
            "user_id": page.user_id,
            "title": page.title,
            "publication_date": page.publication_date,
            "topic_id": topic_row._mapping["id"],
            "page_id": page_id,
        },
    )
    connection.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No page found with ID {page_id}.",
        )
