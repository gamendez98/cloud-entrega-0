from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException
from fastapi import Request, Form

from concerns.authentication import get_current_user
from config import templates
from models.categories import Querier as CategoryQuerier
from models.connection import get_connection
from models.models import State
from models.tasks import Querier, UpdateTaskParams

from fastapi import Depends
from pydantic import BaseModel, field_validator
tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])



def get_categories(connection=Depends(get_connection)):
    category_querier = CategoryQuerier(connection)
    return list(category_querier.get_all_categories())


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
        'request': request, 'task': task, "categories": categories, 'states': State
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
            "user": user, 'states': State
        }
    )


class UpdateTaskParameters(BaseModel):
    description: str
    expected_finished_at: Optional[datetime]
    state: State
    category_id: Optional[int]

    @field_validator('expected_finished_at', mode='before')
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


@tasks_router.put("/{task_id}", name="tasks:update")
async def update_task(
        request: Request,
        task_id: int,
        parameters: Annotated[UpdateTaskParameters, Form()],
        connection=Depends(get_connection),
        categories=Depends(get_categories),
        user=Depends(get_current_user)
):
    querier = Querier(connection)
    task = querier.update_task(
        arg=UpdateTaskParams(
            id=task_id,
            description=parameters.description,
            expected_finished_at=parameters.expected_finished_at,
            state=parameters.state,
            category_id=parameters.category_id,
        )
    )
    if task.person_id != user.id:
        connection.rollback()
        return HTTPException(status_code=403, detail="You are not authorized to update this task.")
    return templates.TemplateResponse('tasks/list_item.html', {
        'request': request, 'task': task, "categories": categories, 'states': State
    })

@tasks_router.get("/category/{category_id}", name="tasks:category")
def get_tasks_by_category(
        request: Request,
        category_id: int,
        connection=Depends(get_connection),
        categories=Depends(get_categories),
        user=Depends(get_current_user)
):
    querier = Querier(connection)
    tasks = querier.get_task_username_and_by_category_id(
        username=user.username,
        category_id=category_id
    )
    category_querier = CategoryQuerier(connection)
    category = category_querier.get_category_by_id(id=category_id)
    return templates.TemplateResponse(
        "tasks/index.html", {
            "request": request, "title": f"Tasks in category {category.name}",
            "tasks": tasks, "categories": categories,
            "user": user, 'states': State
        }
    )

