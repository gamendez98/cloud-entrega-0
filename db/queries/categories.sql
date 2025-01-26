-- name: CreateCategory :one
INSERT INTO categories (name, description)
VALUES ($1, $2)
RETURNING *;

-- name: GetAllCategories :many
SELECT *
FROM categories;

-- name: UpdateCategory :exec
UPDATE categories
SET name        = $2,
    description = $3
WHERE id = $1;

-- name: DeleteCategory :exec
DELETE
FROM categories
WHERE id = $1;