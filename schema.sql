-- SQL CREATE Schema for bookclub.db

DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS book_author;
DROP TABLE IF EXISTS loans;

CREATE TABLE books (
    book_id     INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    published   DATETIME
);

CREATE TABLE members (
    member_id   INTEGER PRIMARY KEY,
    member_name TEXT NOT NULL,
    email       TEXT NOT NULL,
    phone       TEXT NOT NULL,
    joined      DATETIME,
    deleted     INTEGER DEFAULT 0
                CHECK (deleted IN (0,1))
);

CREATE TABLE authors (
    author_id       INTEGER PRIMARY KEY,
    author_name     TEXT NOT NULL
);

CREATE TABLE book_author (
    book_id     INTEGER,
    author_id   INTEGER,
    PRIMARY KEY(book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE loans (
    loan_id     INTEGER PRIMARY KEY,
    member_id   INTEGER NOT NULL,
    book_id     INTEGER NOT NULL,
    loan_date   DATETIME NOT NULL,
    due_date    DATETIME NOT NULL,
    return_date DATETIME,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);