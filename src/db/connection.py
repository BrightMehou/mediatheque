import os

from sqlalchemy import create_engine

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
)

engine = create_engine(DB_URL, future=True)
