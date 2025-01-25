-- name: CreateUser :one
INSERT INTO persons (username, email, password_hash) VALUES ($1, $2, $3)
RETURNING *;

-- name: GetPasswordHash :one
SELECT password_hash FROM persons where persons.username = $1;
