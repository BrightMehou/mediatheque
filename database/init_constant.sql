TRUNCATE livre_type,
auteur,
livre RESTART identity CASCADE;

INSERT INTO
    livre_type (id, TYPE)
VALUES
    (1, 'Roman'),
    (2, 'Nouvelle'),
    (3, 'Essai'),
    (4, 'Théâtre'),
    (5, 'Biographie'),
    (6, 'Recueil'),
    (7, 'Bande dessinée'),
    (8, 'Comics'),
    (9, 'Manga'),
    (10, 'Manhwa'),
    (11, 'Manhua'),
    (12, 'Art / Illustration') ON CONFLICT (id) DO NOTHING;