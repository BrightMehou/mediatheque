INSERT INTO
    livre_type (id, TYPE)
VALUES
    (1, 'Roman'),
    (2, 'Bande dessinée'),
    (3, 'Essai'),
    (4, 'Poésie'),
    (5, 'Manuel scolaire') ON CONFLICT (id) DO NOTHING;

INSERT INTO
    livre_genre (id, genre)
VALUES
    (1, 'Science-Fiction'),
    (2, 'Policier'),
    (3, 'Historique'),
    (4, 'Fantastique'),
    (5, 'Biographie'),
    (6, 'Aventure') ON CONFLICT (id) DO NOTHING;