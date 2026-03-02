import os

from fastapi import APIRouter
from typing import Dict, List
from sqlalchemy import create_engine, text
import pandas as pd

auteur_router = APIRouter(prefix="/auteurs", tags=["auteurs"])

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DB_URL)


@auteur_router.get("/")
def get_auteurs() -> List[Dict]:
    query = "SELECT id, nom, prenom, pseudonyme FROM auteur ORDER BY nom;"
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    return df.to_dict(orient="records")
