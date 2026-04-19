from typing import Dict

from fastapi import FastAPI

from src.api.author import author_router
from src.api.book import book_router
from src.api.book_type import book_type_router

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
