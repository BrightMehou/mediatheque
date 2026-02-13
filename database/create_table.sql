CREATE TABLE IF NOT EXISTS auteur (
    id integer PRIMARY KEY,
    nom varchar,
    prenom varchar,
    pseudonyme varchar
);

CREATE TABLE IF NOT EXISTS livre_type (
    id integer PRIMARY KEY,
    TYPE varchar
);

CREATE TABLE IF NOT EXISTS livre_genre (
    id integer PRIMARY KEY,
    genre varchar
);

CREATE TABLE IF NOT EXISTS livre (
    id integer PRIMARY KEY,
    auteur_id integer REFERENCES auteur(id),
    titre varchar,
    date_publication date,
    genre_id integer REFERENCES livre_genre(id),
    type_id integer REFERENCES livre_type(id),
    nb_pages integer,
    langue varchar
);