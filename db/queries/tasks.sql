-- name: GetTasksByUsername :many
SELECT tasks.*
FROM tasks
         JOIN persons ON tasks.person_id = persons.id AND persons.username = $1;


-- name: GetTaskById :one
SELECT *
FROM tasks
WHERE id = $1;


-- name: CreateTask :one
INSERT INTO tasks (description, person_id, category_id)
VALUES ($1, $2, $3)
RETURNING *;


-- name: UpdateTask :one
UPDATE tasks
SET description          = $1,
    expected_finished_at = $2,
    state                = $3,
    category_id          = $4
WHERE id = $5
RETURNING *;


-- name: DeleteTask :one
DELETE
FROM tasks
WHERE id = $1
RETURNING *;

