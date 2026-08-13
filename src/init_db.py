import logging
import random
from pathlib import Path

from faker import Faker
from sqlalchemy import text
from sqlalchemy.engine import Connection

from db.connection import engine

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


def create_tables(connection: Connection) -> None:
    logger.info("Creating tables...")
    sql_text = SQL_FILE.read_text(encoding="utf-8")
    connection.exec_driver_sql(sql_text)


def truncate_tables(connection: Connection) -> None:
    logger.info("Truncating tables...")
    connection.execute(
        text(
            """
            TRUNCATE TABLE page, users, topic
            RESTART IDENTITY CASCADE
            """
        )
    )


def seed_topics(connection: Connection) -> list[int]:
    logger.info("Inserting topics...")

    connection.execute(
        text("INSERT INTO topic (topic) VALUES (:topic)"),
        [{"topic": topic} for topic in TOPICS],
    )

    return [
        row.id for row in connection.execute(text("SELECT id FROM topic ORDER BY id"))
    ]


def generate_users(count: int = 30) -> list[dict[str, str]]:
    return [
        {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "pseudo": fake.user_name(),
            "email": fake.unique.email(),
            "password": fake.password(),
        }
        for _ in range(count)
    ]


def seed_users(connection: Connection, count: int = 30) -> list[int]:
    logger.info("Inserting users...")

    connection.execute(
        text(
            """
            INSERT INTO users (
                first_name,
                last_name,
                pseudo,
                email,
                password
            )
            VALUES (
                :first_name,
                :last_name,
                :pseudo,
                :email,
                :password
            )
            """
        ),
        generate_users(count),
    )

    return [
        row.id for row in connection.execute(text("SELECT id FROM users ORDER BY id"))
    ]


def generate_pages(
    user_ids: list[int],
    topic_ids: list[int],
    count: int = 1000,
) -> list[dict]:
    return [
        {
            "user_id": random.choice(user_ids),
            "title": fake.sentence(),
            "publication_date": fake.date_between(
                start_date="-10y",
                end_date="today",
            ),
            "content": fake.text(),
            "topic_id": random.choice(topic_ids),
        }
        for _ in range(count)
    ]


def seed_pages(
    connection: Connection,
    user_ids: list[int],
    topic_ids: list[int],
    count: int = 1000,
) -> None:
    logger.info("Inserting pages...")

    connection.execute(
        text(
            """
            INSERT INTO page (
                user_id,
                title,
                publication_date,
                content,
                topic_id
            )
            VALUES (
                :user_id,
                :title,
                :publication_date,
                :content,
                :topic_id
            )
            """
        ),
        generate_pages(user_ids, topic_ids, count),
    )


def initialize_database() -> None:
    logger.info("DB initialization started...")

    with engine.begin() as connection:
        create_tables(connection)
        truncate_tables(connection)

        topic_ids = seed_topics(connection)
        user_ids = seed_users(connection)

        seed_pages(
            connection,
            user_ids=user_ids,
            topic_ids=topic_ids,
        )

    logger.info("DB initialization completed successfully.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    initialize_database()
