from fastapi import APIRouter

from models.connection import get_connection
from models.tasks import Querier

tasks_router = APIRouter(prefix="/users", tags=["Tasks"])

from fastapi import Depends
from pydantic import BaseModel


class CreateTaskParameters(BaseModel):
    title: str
    description: str
    due_date: str


@tasks_router.post("/")
async def create_task(parameters: CreateTaskParameters, connection=Depends(get_connection)):
    querier = Querier(connection)
    task = querier.create_task(
        title=parameters.title,
        description=parameters.description,
        due_date=parameters.due_date,
    )
    return task


@tasks_router.delete("/{task_id}")
async def delete_task(task_id: int, connection=Depends(get_connection)):
    querier = Querier(connection)
    result = querier.delete_task(id=task_id)
    if result:
        return {"message": f"Task with ID {task_id} has been deleted successfully."}
    return {"error": f"Task with ID {task_id} not found."}


@tasks_router.get("user/{username}")
async def get_user_tasks(username: str, connection=Depends(get_connection)):
    querier = Querier(connection)
    tasks = querier.get_tasks_by_username(username=username)
    return tasks
