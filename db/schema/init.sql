CREATE TABLE persons
(
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    image_path    TEXT
);

CREATE TABLE categories
(
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL
);


CREATE TYPE state AS ENUM ('backlog', 'started', 'finished');


CREATE TABLE tasks
(
    id          SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_finished_at TIMESTAMP,
    state state NOT NULL DEFAULT 'backlog',
    person_id INT REFERENCES persons (id),
    category_id INT REFERENCES categories (id)
);