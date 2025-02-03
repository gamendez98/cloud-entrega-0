from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException
from fastapi import Request, Form
from fastapi.responses import HTMLResponse

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


@tasks_router.post("/", name="tasks:create", response_class=HTMLResponse)
async def create_task(
        request: Request,
        parameters: Annotated[CreateTaskParameters, Form()], connection=Depends(get_connection),
        categories=Depends(get_categories),
        user=Depends(get_current_user)
):
    """
    Creates a new task based on the provided parameters and inserts it into the
    database. The newly created task is then rendered in the task list item
    template.

    :param request: The HTTP request object
    :param parameters: Object containing the parameters for task creation,
        such as the description and category ID
    :param connection: The database connection dependency
    :param categories: List of categories fetched via dependency
    :param user: The current authenticated user fetched via dependency
        containing user details like ID
    :return: An HTML response rendering the task list item with the created
        task, available categories, and state information
    """
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
    """
    Deletes a specific task by its unique identifier. This operation ensures the task
    belongs to the authenticated user before permitting deletion. If the task is not found
    or the user does not have authorization, appropriate HTTP exceptions are raised. In
    case of successful deletion, a confirmation message is returned.

    :param task_id: The unique identifier of the task to be deleted.
    :type task_id: int
    :param connection: A database connection dependency that executes queries.
    :param user: The authenticated user attempting to delete a task.
    :return: A confirmation message or error details depending on the task's existence
             and user authorization.
    :rtype: dict | HTTPException
    """
    querier = Querier(connection)
    result = querier.delete_task(id=task_id)
    if result.person_id != user.id:
        connection.rollback()
        return HTTPException(status_code=403, detail="You are not authorized to delete this task.")
    if result:
        return HTTPException(status_code=404, detail=f"Task with ID {task_id} has been deleted successfully.")
    return {"error": f"Task with ID {task_id} not found."}


@tasks_router.get("/", name="tasks:index", response_class=HTMLResponse)
async def get_user_tasks(
        request: Request,
        connection=Depends(get_connection),
        categories=Depends(get_categories),
        user=Depends(get_current_user)
):
    """
    Fetches and displays the tasks associated with the current user. The endpoint
    invokes the necessary dependencies to retrieve user-specific data, including
    tasks, user information, and task categories. This data is then rendered
    into an HTML template for presentation.

    :param request: The HTTP request instance which provides details about
        the incoming user request.
    :param connection: Database connection dependency, used for querying task details.
    :param categories: A list of task categories fetched as an application dependency.
    :param user: The current authenticated user whose tasks are to be retrieved.
    :return: An `HTMLResponse` containing the rendered task list with user-specific
        details and associated categories.
    """
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


@tasks_router.put("/{task_id}", name="tasks:update", response_class=HTMLResponse)
async def update_task(
        request: Request,
        task_id: int,
        parameters: Annotated[UpdateTaskParameters, Form()],
        connection=Depends(get_connection),
        categories=Depends(get_categories),
        user=Depends(get_current_user)
):
    """
    Updates an existing task in the system. The function processes the update
    parameters provided via a form and validates the action based on the
    current user's authorization. If the current user does not have authorization
    to update the task, an HTTP 403 exception is raised.

    :param request: The HTTP request object providing metadata about the HTTP request.
    :type request: Request
    :param task_id: The unique identifier of the task to be updated.
    :type task_id: int
    :param parameters: Form data submitted by the user containing the updates for
        the task, including description, expected finish date, state, and category ID.
    :type parameters: UpdateTaskParameters
    :param connection: The database connection dependency providing a connection
        to the database.
    :param categories: The dependency injecting available task categories for display
        purposes.
    :param user: The dependency providing details of the currently authenticated user.
    :return: A rendered HTML template for the updated task list item.
    :rtype: TemplateResponse
    :raises HTTPException: If the current user is not authorized to update the task.
    """
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

@tasks_router.get("/category/{category_id}", name="tasks:category", response_class=HTMLResponse)
def get_tasks_by_category(
        request: Request,
        category_id: int,
        connection=Depends(get_connection),
        categories=Depends(get_categories),
        user=Depends(get_current_user)
):
    """
    Retrieves tasks for a specific category, identified by its ID, and returns
    an HTML response displaying the tasks alongside additional contextual
    information. It fetches the tasks for the currently authenticated user and
    constructs the response including user's tasks, categories, and state
    information.

    :param request: The current HTTP request object.
    :type request: Request
    :param category_id: The ID of the category to fetch tasks for.
    :type category_id: int
    :param connection: Database connection dependency for performing queries.
    :type connection: depends(get_connection)
    :param categories: List of categories available in the system.
    :type categories: depends(get_categories)
    :param user: The currently authenticated user making the request.
    :type user: depends(get_current_user)
    :return: An HTML response displaying the tasks filtered by the category
        and other necessary information for the UI.
    :rtype: HTMLResponse
    """
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

