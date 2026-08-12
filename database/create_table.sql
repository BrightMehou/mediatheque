CREATE
OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$ BEGIN NEW.updated_at = NOW();

RETURN NEW;

END;

$$ LANGUAGE plpgsql;

DROP TABLE IF EXISTS users CASCADE;

DROP TABLE IF EXISTS topic CASCADE;

DROP TABLE IF EXISTS page CASCADE;

CREATE TABLE IF NOT EXISTS users (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW(),
    deleted_at timestamptz,
    first_name text,
    last_name text,
    pseudonym text NOT NULL,
    email text NOT NULL UNIQUE,
    password text NOT NULL
);

CREATE TABLE IF NOT EXISTS topic (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW(),
    deleted_at timestamptz,
    topic text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS page (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW(),
    deleted_at timestamptz,
    user_id integer REFERENCES users(id) NOT NULL,
    title text NOT NULL,
    publication_date date,
    content text,
    topic_id integer REFERENCES topic(id)
);

DROP TRIGGER IF EXISTS set_updated_at_on_users ON users;

CREATE TRIGGER set_updated_at_on_users BEFORE
UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_on_topic ON topic;

CREATE TRIGGER set_updated_at_on_topic BEFORE
UPDATE
    ON topic FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_on_page ON page;

CREATE TRIGGER set_updated_at_on_page BEFORE
UPDATE
    ON page FOR EACH ROW EXECUTE FUNCTION set_updated_at();