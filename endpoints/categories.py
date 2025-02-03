from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi import Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

from config import templates
from models.categories import Querier
from models.connection import get_connection

category_router = APIRouter(prefix="/categories", tags=["Categories"])


class CreateCategoryParameters(BaseModel):
    name: str
    description: str


@category_router.post("/", name="categories:create", response_class=HTMLResponse)
async def create_category(
        request: Request,
        parameters: Annotated[CreateCategoryParameters, Form()],
        connection=Depends(get_connection)):
    """
    Handles the creation of a new category and renders the category list item page.

    Creates a new category in the database with the provided name and description,
    using the connection dependency to interact with the database. Once the category
    is created successfully, it renders an HTML template showing the created category
    list item.

    :param request: FastAPI Request object, which provides details about the HTTP
        request made by the client.
    :param parameters: Data extracted from the submitted form, representing the new
        category's name and description.
    :param connection: Database connection dependency, resolved by the `get_connection`
        function, allowing interaction with the database.
    :return: Rendered HTML response displaying the newly created category list item.
    """
    querier = Querier(connection)
    category = querier.create_category(
        name=parameters.name,
        description=parameters.description,
    )
    return templates.TemplateResponse('categories/list_item.html', {
        'request': request, 'category': category
    })


@category_router.delete("/{category_id}", name="categories:delete")
async def delete_category(category_id: int, connection=Depends(get_connection)):
    """
    Deletes a category from the database using the provided category ID. This function
    utilizes a dependency to acquire a database connection and interacts with the
    Querier class for performing the deletion operation.

    :param category_id: An integer representing the unique ID of the category to delete.
    :param connection: A database connection acquired through a dependency injection.
    :return: A dictionary containing a success message if the deletion was successful.
                If the category with the given ID does not exist, an HTTPException with
                a 404 status code is raised.
    """
    querier = Querier(connection)
    result = querier.delete_category(id=category_id)
    if result:
        return {"message": f"Category with ID {category_id} has been deleted successfully."}
    return HTTPException(status_code=404, detail=f"Category with ID {category_id} not found.")


@category_router.get("/", name="categories:index", response_class=HTMLResponse)
async def get_all_categories(request: Request, connection=Depends(get_connection)):
    """
    Handles HTTP GET requests to fetch all categories and returns an HTML response
    rendered with the list of categories.

    This function fetches all categories from the database using a `Querier` instance
    and renders them using a specified HTML template. It is designed to work with
    HTTP request handling and assumes appropriate dependencies for its parameters.

    :param request: FastAPI Request object used to extract HTTP request data.
    :param connection: Database connection dependency provided through FastAPI's
        Depends feature.
    :return: HTMLResponse containing rendered template with all categories.
    """
    querier = Querier(connection)
    categories = querier.get_all_categories()
    return templates.TemplateResponse(
        "categories/index.html", {"request": request, "categories": categories}
    )


@category_router.put("/{category_id}", name="categories:update", response_class=HTMLResponse)
async def update_category(
        request: Request,
        category_id: int,
        parameters: Annotated[CreateCategoryParameters, Form()],
        connection=Depends(get_connection)):
    """
    Updates an existing category identified by the provided category ID. This API endpoint
    is responsible for modifying the details of a category, including its name and description.
    If the category exists, it returns the updated category details rendered in an HTML template.
    If the category is not found, it raises an HTTPException with a 404 status code.

    :param request: Request object that provides metadata about the request context.
    :type request: Request
    :param category_id: Integer identifier for a specific category to be updated.
    :type category_id: int
    :param parameters: Contains parameters for creating or updating category, including
        `name` and `description`, provided via an HTML form.
    :type parameters: CreateCategoryParameters
    :param connection: Database connection dependency used to execute queries.
    :type connection: Any
    :return: HTMLResponse with the updated category details rendered in a template if
        the category exists; Otherwise, raises an HTTPException for a non-existent category.
    :rtype: TemplateResponse or HTTPException
    """
    querier = Querier(connection)
    updated_category = querier.update_category(
        id=category_id,
        name=parameters.name,
        description=parameters.description,
    )
    if updated_category:
        return templates.TemplateResponse('categories/list_item.html', {
            'request': request, 'category': updated_category
        })
    return HTTPException(status_code=404, detail=f"Category with ID {category_id} not found.")
