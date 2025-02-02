from typing import Annotated

from fastapi import APIRouter, HTTPException

from concerns.authentication import get_current_user
from config import templates
from models.connection import get_connection
from models.tasks import Querier
from models.categories import Querier as CategoryQuerier
from fastapi import Request, Form

tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])

from fastapi import Depends
from pydantic import BaseModel


def get_categories(connection=Depends(get_connection)):
    category_querier = CategoryQuerier(connection)
    return category_querier.get_all_categories()


class CreateTaskParameters(BaseModel):
    description: str
    category_id: int


@tasks_router.post("/", name="tasks:create")
async def create_task(
        request: Request,
        parameters: Annotated[CreateTaskParameters, Form()], connection=Depends(get_connection),
        categories=Depends(get_categories),
        user=Depends(get_current_user)
):
    querier = Querier(connection)
    task = querier.create_task(
        description=parameters.description,
        person_id=user.id,
        category_id=parameters.category_id,
    )
    return templates.TemplateResponse('tasks/list_item.html', {
        'request': request, 'task': task, "categories": categories
    })


@tasks_router.delete("/{task_id}", name="tasks:delete")
async def delete_task(
        task_id: int,
        connection=Depends(get_connection),
        user=Depends(get_current_user)
):
    querier = Querier(connection)
    result = querier.delete_task(id=task_id)
    if result.person_id != user.id:
        connection.rollback()
        return HTTPException(status_code=403, detail="You are not authorized to delete this task.")
    if result:
        return HTTPException(status_code=404, detail=f"Task with ID {task_id} has been deleted successfully.")
    return {"error": f"Task with ID {task_id} not found."}


@tasks_router.get("/", name="tasks:index")
async def get_user_tasks(
        request: Request,
        connection=Depends(get_connection),
        categories=Depends(get_categories),
        user=Depends(get_current_user)
):
    querier = Querier(connection)
    tasks = querier.get_tasks_by_username(username=user.username)
    return templates.TemplateResponse(
        "tasks/index.html", {
            "request": request, "title": "All tasks",
            "tasks": tasks, "categories": categories,
            "user": user
        }
    )
