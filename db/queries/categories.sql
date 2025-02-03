-- name: CreateCategory :one
INSERT INTO categories (name, description)
VALUES ($1, $2)
RETURNING *;

-- name: GetAllCategories :many
SELECT *
FROM categories;

-- name: GetCategoryById :one
SELECT *
FROM categories
WHERE categories.id = $1;

-- name: UpdateCategory :one
UPDATE categories
SET name        = $2,
    description = $3
WHERE id = $1
RETURNING *;

-- name: DeleteCategory :one
DELETE
FROM categories
WHERE id = $1
RETURNING *;