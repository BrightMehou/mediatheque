from typing import Dict

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.api.author import author_router
from src.api.book import book_router
from src.api.book_type import book_type_router
from src.db.connection import get_db

app = FastAPI(
    title="Médiathèque API",
    description="API pour la gestion de la médiathèque",
    version="0.2.0",
)

app.include_router(author_router)
app.include_router(book_type_router)
app.include_router(book_router)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"msg": "API de la médiathèque opérationnelle ✅"}


@app.get("/health")
def health_check(connection: Connection = Depends(get_db)) -> Dict[str, str]:
    try:
        connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"DB inaccessible: {exc}")
    return {"status": "ok", "db": "ok"}
