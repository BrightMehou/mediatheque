CREATE TABLE IF NOT EXISTS auteur (
    id integer PRIMARY KEY,
    nom varchar,
    prenom varchar,
    pseudonyme varchar NOT NULL
);

CREATE TABLE IF NOT EXISTS livre_type (
    id integer PRIMARY KEY,
    TYPE varchar NOT NULL
);

CREATE TABLE IF NOT EXISTS livre (
    id integer PRIMARY KEY,
    auteur_id integer REFERENCES auteur(id) NOT NULL,
    titre varchar NOT NULL,
    isbn varchar NOT NULL,
    date_publication date,
    type_id integer REFERENCES livre_type(id),
    nb_pages integer
);