from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.db.connection import get_db


class TopicBase(BaseModel):
    topic: str


class TopicCreate(TopicBase):
    pass


class TopicUpdate(TopicBase):
    pass


class TopicOut(TopicBase):
    id: int


topic_router = APIRouter(prefix="/topic", tags=["topic"])


@topic_router.get("/", response_model=list[TopicOut])
def get_topics(connection: Annotated[Connection, Depends(get_db)]):
    query = "SELECT id, topic FROM topic ORDER BY topic;"
    result = connection.execute(text(query))
    return result.mappings().all()


@topic_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=dict[str, int],
)
def create_topic(
    topic: TopicCreate,
    connection: Annotated[Connection, Depends(get_db)],
):
    query = "INSERT INTO topic (topic) VALUES (:topic) RETURNING id;"
    result = connection.execute(text(query), {"topic": topic.topic})

    new_id = result.scalar()
    connection.commit()

    return {"id": new_id}


@topic_router.put("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_topic(
    topic_id: int,
    topic: TopicUpdate,
    connection: Annotated[Connection, Depends(get_db)],
):
    query = "UPDATE topic SET topic = :new_topic WHERE id = :topic_id;"
    result = connection.execute(
        text(query),
        {"topic_id": topic_id, "new_topic": topic.topic},
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No topic found with ID {topic_id}.",
        )
    connection.commit()


@topic_router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: int, connection: Annotated[Connection, Depends(get_db)]):
    query = "DELETE FROM topic WHERE id = :topic_id;"
    result = connection.execute(text(query), {"topic_id": topic_id})

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No page type found with ID {topic_id}.",
        )
    connection.commit()
