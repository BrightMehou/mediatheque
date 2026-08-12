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
    pseudonym: str
    publication_date: date
    topic: str


page_router = APIRouter(prefix="/page", tags=["page"])


@page_router.get("/", response_model=list[pageOut])
def load_pages(
    connection: Annotated[Connection, Depends(get_db)],
    topics: Annotated[list[str] | None, Query()] = None,
    user: str | None = None,
):
    query = """
    SELECT p.id, p.title, u.pseudonym AS pseudonym, p.publication_date, lt.topic
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
        query += " AND u.pseudonym ILIKE :user"
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
    type_query = "SELECT id FROM topic WHERE topic = :topic;"

    insert_query = """
    INSERT INTO page (
        user_id, title, publication_date, topic_id
    )
    VALUES (
        :user_id, :title, :publication_date, :topic_id
    ) RETURNING id;
    """

    type_result = connection.execute(text(type_query), {"topic": page.topic})
    type_row = type_result.fetchone()

    if type_row is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid page topic: '{page.topic}' does not exist.",
        )

    result = connection.execute(
        text(insert_query),
        {
            "user_id": page.user_id,
            "title": page.title,
            "isbn": str(page.isbn),
            "publication_date": page.publication_date,
            "topic_id": type_row._mapping["id"],
            "page_count": page.page_count,
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
    type_query = "SELECT id FROM topic WHERE topic = :topic;"

    update_query = """
    UPDATE page
    SET user_id = :user_id,
        title = :title,
        publication_date = :publication_date,
        topic_id = :topic_id,
    WHERE id = :page_id;
    """

    type_result = connection.execute(text(type_query), {"topic": page.topic})
    type_row = type_result.fetchone()

    if type_row is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid page topic: '{page.topic}' does not exist.",
        )

    result = connection.execute(
        text(update_query),
        {
            "user_id": page.user_id,
            "title": page.title,
            "isbn": str(page.isbn),
            "publication_date": page.publication_date,
            "topic_id": type_row._mapping["id"],
            "page_count": page.page_count,
            "page_id": page_id,
        },
    )
    connection.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No page found with ID {page_id}.",
        )
