from fastapi import FastAPI, Query
from typing import List, Dict
from sqlalchemy import create_engine, text
import pandas as pd
import os

app = FastAPI(
    title="Médiathèque API",
    description="API pour la gestion d'une médiathèque",
    version="0.1.0",
)

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

engine = create_engine(DB_URL)

@app.get("/")
async def root() -> Dict[str, str]:
    return {"msg": "API de la médiathèque opérationnelle ✅"}

@app.get("/types")
def load_types() -> List[str]:
    query = "SELECT type FROM livre_type ORDER BY type;"
    
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    return df['type'].tolist()

@app.get("/livres")
def load_livres(types: List[str] = Query(default=None)) -> List[dict]:

    query = """
    SELECT l.id, l.titre, a.pseudonyme AS auteur, l.date_publication, lt.type
    FROM livre l
    JOIN auteur a ON l.auteur_id = a.id
    JOIN livre_type lt ON l.type_id = lt.id
    """
    if not types:
        query += " ORDER BY l.titre LIMIT 100"
    else:
        types = ",".join(f"'{x}'" for x in types)
        query += f" WHERE lt.type IN ({types}) ORDER BY l.titre LIMIT 100"

    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    
    return df.to_dict(orient='records')