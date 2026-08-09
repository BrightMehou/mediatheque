import logging
import os
from collections.abc import Generator

from sqlalchemy import URL, Connection, create_engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

DB_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "postgres"),
)

engine = create_engine(DB_URL, future=True)


def get_db() -> Generator[Connection]:
    connection = engine.connect()
    try:
        yield connection
    except SQLAlchemyError:
        logger.exception("Erreur de base de données")
        raise
    finally:
        connection.close()
