import os
from typing import Dict, List

import pandas as pd
from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
from src.api.auteur import auteur_router
from src.api.livre_type import livre_type_router

app = FastAPI(
    title="Médiathèque API",
    description="API pour la gestion d'une médiathèque",
    version="0.2.0",
)

app.include_router(auteur_router)
app.include_router(livre_type_router)
DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DB_URL)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"msg": "API de la médiathèque opérationnelle ✅"}


@app.get("/livres")
def load_livres(
    types: List[str] = Query(default=None), auteur: str = None
) -> List[dict]:

    query = """
    SELECT l.id, l.titre, a.pseudonyme AS auteur, l.date_publication, lt.type
    FROM livre l
    JOIN auteur a ON l.auteur_id = a.id
    JOIN livre_type lt ON l.type_id = lt.id
    WHERE 1=1
    """

    if types:
        type_list = ", ".join(f"'{t}'" for t in types)
        query += f" AND lt.type IN ({type_list})"

    if auteur:
        query += f" AND a.pseudonyme ilike '%{auteur}%'"

    query += " LIMIT 100;"

    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)

    return df.to_dict(orient="records")
