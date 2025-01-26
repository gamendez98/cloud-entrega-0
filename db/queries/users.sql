-- name: CreateUser :one
INSERT INTO persons (username, email, password_hash)
VALUES ($1, $2, $3)
RETURNING *;

-- name: GetPasswordHash :one
SELECT password_hash
FROM persons
where persons.username = $1;

-- name: SaveImagePath :exec

-- Updates the image_path field for a specified user
UPDATE persons
SET image_path = $1
WHERE username = $2;

-- name: GetUserByUsername :one
SELECT *
FROM persons
WHERE username = $1;


