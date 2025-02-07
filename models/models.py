# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.27.0
import dataclasses
import datetime
import enum
from typing import Optional


class State(str, enum.Enum):
    BACKLOG = "backlog"
    STARTED = "started"
    FINISHED = "finished"


@dataclasses.dataclass()
class Category:
    id: int
    name: str
    description: str


@dataclasses.dataclass()
class Person:
    id: int
    username: str
    email: str
    password_hash: str
    image_path: Optional[str]


@dataclasses.dataclass()
class Task:
    id: int
    description: str
    created_at: Optional[datetime.datetime]
    expected_finished_at: Optional[datetime.datetime]
    state: State
    person_id: Optional[int]
    category_id: Optional[int]
