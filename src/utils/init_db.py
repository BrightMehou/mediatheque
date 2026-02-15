from faker import Faker
import psycopg2
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

fake = Faker('fr_FR')
Faker.seed(42)

logger.info("Connexion à la base de données...")
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

logger.info("Insertion des auteurs")
cur.executemany(
    "INSERT INTO auteur (id, nom, prenom, pseudonyme) VALUES (%s, %s, %s, %s)",
    [(i, fake.last_name(), fake.first_name(), fake.user_name()) for i in range(1, 11)]
)

logger.info("Insertion des livres")
cur.executemany(
    "INSERT INTO livre (id, auteur_id, titre, isbn, date_publication, type_id, nb_pages) VALUES (%s, %s, %s, %s, %s, %s, %s)",
    [(i, fake.random_int(min=1, max=10), fake.sentence(), fake.isbn13(), fake.date_between(start_date='-10y', end_date='today'), fake.random_int(min=1, max=12), fake.random_int(min=50, max=500)) for i in range(1, 101)]
)

conn.commit()
logger.info("Deconnexion de la base de données...")
cur.close()
conn.close()

