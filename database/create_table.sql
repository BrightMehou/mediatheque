CREATE TABLE IF NOT EXISTS author (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom varchar,
    prenom varchar,
    pseudonyme varchar NOT NULL
);

CREATE TABLE IF NOT EXISTS book_type (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    TYPE varchar NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    auteur_id integer REFERENCES author(id) NOT NULL,
    titre varchar NOT NULL,
    isbn varchar NOT NULL,
    date_publication date,
    type_id integer REFERENCES book_type(id),
    nb_pages integer
);