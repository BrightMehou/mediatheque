import logging
import random
from pathlib import Path

from faker import Faker
from sqlalchemy import text

from db.connection import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

fake = Faker("fr_FR")
Faker.seed(42)

BASE_DIR = Path(__file__).resolve().parent
SQL_FILE = BASE_DIR.parent / "database" / "create_table.sql"

LIVRE_TYPES = [
    "Art / Illustration",
    "Bande dessinée",
    "Biographie",
    "Comics",
    "Essai",
    "Manga",
    "Manhwa",
    "Manhua",
    "Nouvelle",
    "Recueil",
    "Roman",
    "Théâtre",
]

if __name__ == "__main__":
    logger.info("Connexion à la base de données...")

    with engine.begin() as connection:
        logger.info("Création des tables...")
        sql_text = SQL_FILE.read_text(encoding="utf-8")
        connection.exec_driver_sql(sql_text)

        logger.info("Truncating tables...")
        connection.execute(
            text("TRUNCATE TABLE book, author, book_type RESTART IDENTITY CASCADE"),
        )

        logger.info("Insertion des types de livres")
        connection.execute(
            text("INSERT INTO book_type (type) VALUES (:type)"),
            [{"type": type_name} for type_name in LIVRE_TYPES],
        )

        logger.info("Insertion des auteurs")
        connection.execute(
            text(
                "INSERT INTO author (first_name, last_name, pseudonym) VALUES (:first_name, :last_name, :pseudonym)",
            ),
            [
                {
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "pseudonym": fake.user_name(),
                }
                for _ in range(100)
            ],
        )

        author_ids = [
            row._mapping["id"]
            for row in connection.execute(
                text("SELECT id FROM author ORDER BY id"),
            ).fetchall()
        ]

        book_type_ids = [
            row._mapping["id"]
            for row in connection.execute(
                text("SELECT id FROM book_type ORDER BY id"),
            ).fetchall()
        ]

        logger.info("Insertion des livres")
        connection.execute(
            text(
                "INSERT INTO book (author_id, title, isbn, publication_date, type_id, page_count) "
                "VALUES (:author_id, :title, :isbn, :publication_date, :type_id, :page_count)",
            ),
            [
                {
                    "author_id": random.choice(author_ids),
                    "title": fake.sentence(),
                    "isbn": fake.isbn13(separator=""),
                    "publication_date": fake.date_between(
                        start_date="-10y",
                        end_date="today",
                    ),
                    "type_id": random.choice(book_type_ids),
                    "page_count": fake.random_int(min=50, max=500),
                }
                for _ in range(5000)
            ],
        )

    logger.info("Deconnexion de la base de données...")
