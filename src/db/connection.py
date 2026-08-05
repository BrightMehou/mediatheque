import os

from sqlalchemy import URL, create_engine

DB_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "postgres"),
)

engine = create_engine(DB_URL, future=True)


def get_db():
    with engine.connect() as connection:
        yield connection
