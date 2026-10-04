CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    description TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users,
    book_id INTEGER NOT NULL REFERENCES books ON DELETE CASCADE
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    UNIQUE (type, name)
);

CREATE TABLE book_categories (
    book_id INTEGER NOT NULL REFERENCES books ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories,
    PRIMARY KEY (book_id, category_id)
);

INSERT INTO categories (type, name) VALUES
    ('Genre', 'Fantasia'),
    ('Genre', 'Scifi'),
    ('Genre', 'Historia'),
    ('Genre', 'Elämäkerta'),
    ('Genre', 'Muu'),
    ('Kieli', 'Suomi'),
    ('Kieli', 'Englanti'),
    ('Kieli', 'Ruotsi'),
    ('Kieli', 'Muu');