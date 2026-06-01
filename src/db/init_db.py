import logging
import os

import psycopg
from faker import Faker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
fake = Faker("fr_FR")
Faker.seed(42)

LIVRE_TYPES = [
    ("Roman",),
    ("Nouvelle",),
    ("Essai",),
    ("Théâtre",),
    ("Biographie",),
    ("Recueil",),
    ("Bande dessinée",),
    ("Comics",),
    ("Manga",),
    ("Manhwa",),
    ("Manhua",),
    ("Art / Illustration",),
]

if __name__ == "__main__":
    logger.info("Connexion à la base de données...")
    with (
        psycopg.connect(
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
        ) as conn,
        conn.cursor() as cur,
    ):
        logger.info("Création des tables...")
        with open("database/create_table.sql", "r", encoding="utf-8") as f:
            cur.execute(f.read())
        logger.info("Truncating tables...")
        cur.execute("TRUNCATE TABLE book, author, book_type RESTART IDENTITY CASCADE")
        logger.info("Insertion des types de livres")
        cur.executemany("INSERT INTO book_type (type) VALUES (%s)", LIVRE_TYPES)
        logger.info("Insertion des auteurs")
        cur.executemany(
            "INSERT INTO author (first_name, last_name, pseudonym) VALUES (%s, %s, %s)",
            [
                (fake.first_name(), fake.last_name(), fake.user_name())
                for _ in range(10)
            ],
        )
        logger.info("Insertion des livres")
        cur.executemany(
            """INSERT INTO book
            (author_id, title, isbn, publication_date, type_id, page_count)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            [
                (
                    fake.random_int(min=1, max=10),
                    fake.sentence(),
                    fake.isbn13(separator=""),
                    fake.date_between(start_date="-10y", end_date="today"),
                    fake.random_int(min=1, max=12),
                    fake.random_int(min=50, max=500),
                )
                for _ in range(100)
            ],
        )
    logger.info("Deconnexion de la base de données...")
