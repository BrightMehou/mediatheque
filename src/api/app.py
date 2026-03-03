from typing import Dict

from fastapi import FastAPI

from src.api.auteur import auteur_router
from src.api.livre import livre_router
from src.api.livre_type import livre_type_router

app = FastAPI(
    title="Médiathèque API",
    description="API pour la gestion d'une médiathèque",
    version="0.2.0",
)

app.include_router(auteur_router)
app.include_router(livre_type_router)
app.include_router(livre_router)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"msg": "API de la médiathèque opérationnelle ✅"}
