# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.27.0
# source: categories.sql
from typing import AsyncIterator, Iterator, Optional

import sqlalchemy
import sqlalchemy.ext.asyncio

from models import models


CREATE_CATEGORY = """-- name: create_category \\:one
INSERT INTO categories (name, description)
VALUES (:p1, :p2)
RETURNING id, name, description
"""


DELETE_CATEGORY = """-- name: delete_category \\:exec
DELETE
FROM categories
WHERE id = :p1
"""


GET_ALL_CATEGORIES = """-- name: get_all_categories \\:many
SELECT id, name, description
FROM categories
"""


UPDATE_CATEGORY = """-- name: update_category \\:exec
UPDATE categories
SET name        = :p2,
    description = :p3
WHERE id = :p1
"""


class Querier:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self._conn = conn

    def create_category(self, *, name: str, description: str) -> Optional[models.Category]:
        row = self._conn.execute(sqlalchemy.text(CREATE_CATEGORY), {"p1": name, "p2": description}).first()
        if row is None:
            return None
        return models.Category(
            id=row[0],
            name=row[1],
            description=row[2],
        )

    def delete_category(self, *, id: int) -> None:
        self._conn.execute(sqlalchemy.text(DELETE_CATEGORY), {"p1": id})

    def get_all_categories(self) -> Iterator[models.Category]:
        result = self._conn.execute(sqlalchemy.text(GET_ALL_CATEGORIES))
        for row in result:
            yield models.Category(
                id=row[0],
                name=row[1],
                description=row[2],
            )

    def update_category(self, *, id: int, name: str, description: str) -> None:
        self._conn.execute(sqlalchemy.text(UPDATE_CATEGORY), {"p1": id, "p2": name, "p3": description})


class AsyncQuerier:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def create_category(self, *, name: str, description: str) -> Optional[models.Category]:
        row = (await self._conn.execute(sqlalchemy.text(CREATE_CATEGORY), {"p1": name, "p2": description})).first()
        if row is None:
            return None
        return models.Category(
            id=row[0],
            name=row[1],
            description=row[2],
        )

    async def delete_category(self, *, id: int) -> None:
        await self._conn.execute(sqlalchemy.text(DELETE_CATEGORY), {"p1": id})

    async def get_all_categories(self) -> AsyncIterator[models.Category]:
        result = await self._conn.stream(sqlalchemy.text(GET_ALL_CATEGORIES))
        async for row in result:
            yield models.Category(
                id=row[0],
                name=row[1],
                description=row[2],
            )

    async def update_category(self, *, id: int, name: str, description: str) -> None:
        await self._conn.execute(sqlalchemy.text(UPDATE_CATEGORY), {"p1": id, "p2": name, "p3": description})
