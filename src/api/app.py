from fastapi import FastAPI
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
async def root() -> dict[str, str]:
    return {"msg": "API de la médiathèque opérationnelle ✅"}

@app.get("/genres")
def load_genres() -> list[str]:
    query = "SELECT genre FROM livre_genre ORDER BY genre;"
    
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    return df['genre'].tolist()

@app.get("/types")
def load_types() -> list[str]:
    query = "SELECT type FROM livre_type ORDER BY type;"
    
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    return df['type'].tolist()