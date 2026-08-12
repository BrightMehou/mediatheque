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
SQL_FILE = BASE_DIR.parent / "src" / "db" / "create_table.sql"

TOPICS = [
    "Art",
    "Culture",
    "Économie",
    "Éducation",
    "Environnement",
    "Géographie",
    "Histoire",
    "Informatique",
    "Langues",
    "Littérature",
    "Médecine",
    "Philosophie",
    "Politique",
    "Religion",
    "Sciences",
    "Société",
    "Sports",
    "Technologie",
    "Transports",
    "Vie quotidienne",
]

if __name__ == "__main__":
    logger.info("DB initialization started...")

    with engine.begin() as connection:
        logger.info("TABLE CREATION")
        sql_text = SQL_FILE.read_text(encoding="utf-8")
        connection.exec_driver_sql(sql_text)

        logger.info("Truncating tables...")
        connection.execute(
            text("TRUNCATE TABLE page, users, topic RESTART IDENTITY CASCADE"),
        )

        logger.info("Topics insertion")
        connection.execute(
            text("INSERT INTO topic (topic) VALUES (:topic)"),
            [{"topic": topic_name} for topic_name in TOPICS],
        )

        logger.info("Users insertion")
        connection.execute(
            text(
                "INSERT INTO users (first_name, last_name, pseudo, email, password) VALUES (:first_name, :last_name, :pseudo, :email, :password)",
            ),
            [
                {
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "pseudo": fake.user_name(),
                    "email": fake.unique.email(),
                    "password": fake.password(),
                }
                for _ in range(30)
            ],
        )

        users_ids = [
            row._mapping["id"]
            for row in connection.execute(
                text("SELECT id FROM users ORDER BY id"),
            ).fetchall()
        ]

        topic_ids = [
            row._mapping["id"]
            for row in connection.execute(
                text("SELECT id FROM topic ORDER BY id"),
            ).fetchall()
        ]

        logger.info("Pages insertion")
        connection.execute(
            text(
                "INSERT INTO page (user_id, title, publication_date, content, topic_id) "
                "VALUES (:user_id, :title, :publication_date, :content, :topic_id)",
            ),
            [
                {
                    "user_id": random.choice(users_ids),
                    "title": fake.sentence(),
                    "publication_date": fake.date_between(
                        start_date="-10y",
                        end_date="today",
                    ),
                    "content": fake.text(),
                    "topic_id": random.choice(topic_ids),
                }
                for _ in range(1000)
            ],
        )

    logger.info("DB initialization completed successfully.")
