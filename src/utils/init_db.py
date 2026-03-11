import logging

import psycopg
from faker import Faker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

fake = Faker("fr_FR")
Faker.seed(42)

logger.info("Connexion à la base de données...")
dsn = "dbname=postgres user=postgres password=postgres host=localhost port=5432"

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

with psycopg.connect(dsn) as conn, conn.cursor() as cur:

    logger.info("Truncating tables...")
    cur.execute("TRUNCATE TABLE livre, auteur, livre_type RESTART IDENTITY CASCADE")

    logger.info("Insertion des types de livres")
    cur.executemany("INSERT INTO livre_type (type) VALUES (%s)", LIVRE_TYPES)

    logger.info("Insertion des auteurs")
    cur.executemany(
        "INSERT INTO auteur (nom, prenom, pseudonyme) VALUES (%s, %s, %s)",
        [(fake.last_name(), fake.first_name(), fake.user_name()) for _ in range(10)],
    )

    logger.info("Insertion des livres")
    cur.executemany(
        """INSERT INTO livre
        (auteur_id, titre, isbn, date_publication, type_id, nb_pages)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        [
            (
                fake.random_int(min=1, max=10),
                fake.sentence(),
                fake.isbn13(),
                fake.date_between(start_date="-10y", end_date="today"),
                fake.random_int(min=1, max=12),
                fake.random_int(min=50, max=500),
            )
            for _ in range(100)
        ],
    )

logger.info("Deconnexion de la base de données...")
