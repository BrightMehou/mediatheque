import os
from datetime import date
from typing import Dict, List

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, text


class LivreBase(BaseModel):
    titre: str
    auteur: int
    isbn: str
    date_publication: date
    type: str
    nb_pages: int


class Livre(LivreBase):
    id: int


livre_router = APIRouter(prefix="/livre", tags=["livre"])

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

engine = create_engine(DB_URL)


def validate_isbn(isbn: str) -> bool:
    cleaned = isbn.replace("-", "").replace(" ", "")
    if len(cleaned) == 10:
        if not cleaned[:9].isdigit() or not (
            cleaned[9].isdigit() or cleaned[9] in "Xx"
        ):
            return False

        total = 0
        for index, char in enumerate(cleaned):
            value = 10 - index
            if index == 9 and char in "Xx":
                total += 10
            else:
                total += int(char) * value
        return total % 11 == 0

    if len(cleaned) == 13 and cleaned.isdigit():
        total = 0
        for index, char in enumerate(cleaned):
            weight = 1 if index % 2 == 0 else 3
            total += int(char) * weight
        return total % 10 == 0

    return False


@livre_router.get("/")
def load_livres(
    types: List[str] = Query(default=None), auteur: str = None
) -> List[Dict]:

    query = """
    SELECT l.id, l.titre, a.pseudonyme AS auteur, l.date_publication, lt.type
    FROM livre l
    JOIN auteur a ON l.auteur_id = a.id
    JOIN livre_type lt ON l.type_id = lt.id
    WHERE 1=1
    """

    if types:
        type_list = ", ".join(f"'{t}'" for t in types)
        query += f" AND lt.type IN ({type_list})"

    if auteur:
        query += f" AND a.pseudonyme ilike '%{auteur}%'"

    query += " LIMIT 100;"

    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)

    return df.to_dict(orient="records")


@livre_router.post("/")
def create_livre(livre: LivreBase) -> Dict[str, str]:
    type_query = "SELECT id FROM livre_type WHERE type = :type;"
    insert_query = """
    INSERT INTO livre (auteur_id, titre, isbn, date_publication, type_id, nb_pages)
    VALUES (:auteur_id, :titre, :isbn, :date_publication, :type_id, :nb_pages);
    """

    if not validate_isbn(livre.isbn):
        raise HTTPException(
            status_code=422, detail="ISBN invalide ou format non supporté."
        )

    with engine.connect() as connection:
        type_result = connection.execute(text(type_query), {"type": livre.type})
        type_row = type_result.fetchone()
        if type_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Type de livre '{livre.type}' introuvable.",
            )
        connection.execute(
            text(insert_query),
            {
                "auteur_id": livre.auteur,
                "titre": livre.titre,
                "isbn": livre.isbn,
                "date_publication": livre.date_publication,
                "type_id": type_row._mapping["id"],
                "nb_pages": livre.nb_pages,
            },
        )
        connection.commit()

    return {"message": f"Livre '{livre.titre}' créé avec succès."}


@livre_router.put("/{livre_id}")
def update_livre(livre_id: int, livre: LivreBase) -> Dict[str, str]:
    type_query = "SELECT id FROM livre_type WHERE type = :type;"
    update_query = """
    UPDATE livre
    SET auteur_id = :auteur_id,
        titre = :titre,
        isbn = :isbn,
        date_publication = :date_publication,
        type_id = :type_id,
        nb_pages = :nb_pages
    WHERE id = :livre_id;
    """

    if not validate_isbn(livre.isbn):
        raise HTTPException(
            status_code=422, detail="ISBN invalide ou format non supporté."
        )

    with engine.connect() as connection:
        type_result = connection.execute(text(type_query), {"type": livre.type})
        type_row = type_result.fetchone()
        if type_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Type de livre '{livre.type}' introuvable.",
            )

        result = connection.execute(
            text(update_query),
            {
                "auteur_id": livre.auteur,
                "titre": livre.titre,
                "isbn": livre.isbn,
                "date_publication": livre.date_publication,
                "type_id": type_row._mapping["id"],
                "nb_pages": livre.nb_pages,
                "livre_id": livre_id,
            },
        )
        connection.commit()
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun livre trouvé avec l'ID {livre_id}.",
        )

    return {"message": f"Livre avec l'ID {livre_id} mis à jour avec succès."}
