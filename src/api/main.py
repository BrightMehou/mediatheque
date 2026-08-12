import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.api.book import book_router
from src.api.book_type import book_type_router
from src.api.user import user_router
from src.db.connection import get_db

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Médiathèque API",
    description="API pour la gestion de la médiathèque",
    version="0.3.0",
)

app.include_router(user_router)
app.include_router(book_type_router)
app.include_router(book_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"msg": "API de la médiathèque opérationnelle."}


@app.get("/health")
def health_check(connection: Annotated[Connection, Depends(get_db)]) -> dict[str, str]:
    try:
        connection.execute(text("SELECT 1"))
    except Exception as exc:
        logger.exception("Erreur de connexion à la base de données : %s")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service indisponible (Erreur de base de données).",
        ) from exc

    return {"status": "ok", "db": "ok"}
