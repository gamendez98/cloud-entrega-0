# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.27.0
import dataclasses
from typing import Optional


@dataclasses.dataclass()
class Person:
    id: int
    username: str
    email: str
    password_hash: str
    image_path: Optional[str]
