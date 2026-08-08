CREATE
OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$ BEGIN NEW.updated_at = NOW();

RETURN NEW;

END;

$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS author (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW(),
    deleted_at timestamptz,
    first_name text,
    last_name text,
    pseudonym text NOT NULL
);

CREATE TABLE IF NOT EXISTS book_type (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW(),
    deleted_at timestamptz,
    type text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW(),
    deleted_at timestamptz,
    author_id integer REFERENCES author(id) NOT NULL,
    title text NOT NULL,
    isbn text NOT NULL,
    publication_date date,
    type_id integer REFERENCES book_type(id),
    page_count integer
);

DROP TRIGGER IF EXISTS set_updated_at_on_author ON author;

CREATE TRIGGER set_updated_at_on_author BEFORE
UPDATE
    ON author FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_on_book_type ON book_type;

CREATE TRIGGER set_updated_at_on_book_type BEFORE
UPDATE
    ON book_type FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_on_book ON book;

CREATE TRIGGER set_updated_at_on_book BEFORE
UPDATE
    ON book FOR EACH ROW EXECUTE FUNCTION set_updated_at();