CREATE TABLE users
(
    id            SERIAL PRIMARY KEY,   -- Unique identifier for the user
    username      TEXT NOT NULL UNIQUE, -- Unique username for the user
    email         TEXT NOT NULL UNIQUE, -- Unique email for the user
    password_hash TEXT NOT NULL         -- Hashed password for secure storage
);