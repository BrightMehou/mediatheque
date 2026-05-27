CREATE TABLE IF NOT EXISTS author (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    last_name varchar,
    first_name varchar,
    pseudonym varchar NOT NULL
);

CREATE TABLE IF NOT EXISTS book_type (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type varchar NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    author_id integer REFERENCES author(id) NOT NULL,
    title varchar NOT NULL,
    isbn varchar NOT NULL,
    publication_date date,
    type_id integer REFERENCES book_type(id),
    page_count integer
);