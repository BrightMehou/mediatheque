TRUNCATE livre_type,
auteur,
livre RESTART identity CASCADE;

INSERT INTO
    livre_type (TYPE)
VALUES
    ('Roman'),
    ('Nouvelle'),
    ('Essai'),
    ('Théâtre'),
    ('Biographie'),
    ('Recueil'),
    ('Bande dessinée'),
    ('Comics'),
    ('Manga'),
    ('Manhwa'),
    ('Manhua'),
    ('Art / Illustration');