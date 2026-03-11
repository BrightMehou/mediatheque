import os
from datetime import date
from typing import Dict, List

import pandas as pd
from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, text

class LivreBase(BaseModel):
    titre: str
    auteur: int
    isbn: str
    date_publication: date
    type: str
    nb_pages: int


class Livre(LivreBase):
    id: int

livre_router = APIRouter(prefix="/livre", tags=["livre"])

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DB_URL)


@livre_router.get("/")
def load_livres(
    types: List[str] = Query(default=None), auteur: str = None
) -> List[Dict]:

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
