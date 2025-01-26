-- name: GetTasksByUsername :many
SELECT tasks.*
FROM tasks
         JOIN persons ON tasks.person_id = persons.id AND persons.username = $1;


-- name: CreateTask :one

INSERT INTO tasks (description, person_id, category_id)
VALUES ($1, $2, $3)
RETURNING *;

