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
            text("TRUNCATE TABLE book, users, book_type RESTART IDENTITY CASCADE"),
        )

        logger.info("Insertion des types de livres")
        connection.execute(
            text("INSERT INTO book_type (type) VALUES (:type)"),
            [{"type": type_name} for type_name in LIVRE_TYPES],
        )

        logger.info("Insertion des utilisateurs")
        connection.execute(
            text(
                "INSERT INTO users (first_name, last_name, pseudonym, email, password) VALUES (:first_name, :last_name, :pseudonym, :email, :password)",
            ),
            [
                {
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "pseudonym": fake.user_name(),
                    "email": fake.unique.email(),
                    "password": fake.password(),
                }
                for _ in range(100)
            ],
        )

        users_ids = [
            row._mapping["id"]
            for row in connection.execute(
                text("SELECT id FROM users ORDER BY id"),
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
                "INSERT INTO book (user_id, title, publication_date, type_id) "
                "VALUES (:user_id, :title, :publication_date, :type_id)",
            ),
            [
                {
                    "user_id": random.choice(users_ids),
                    "title": fake.sentence(),
                    "publication_date": fake.date_between(
                        start_date="-10y",
                        end_date="today",
                    ),
                    "type_id": random.choice(book_type_ids),
                }
                for _ in range(5000)
            ],
        )

    logger.info("Deconnexion de la base de données...")
