
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