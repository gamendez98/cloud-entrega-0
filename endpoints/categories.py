from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi import Request
from pydantic import BaseModel

from config import templates
from models.categories import Querier
from models.connection import get_connection

category_router = APIRouter(prefix="/categories", tags=["Categories"])


class CreateCategoryParameters(BaseModel):
    name: str
    description: str


@category_router.post("/", name="categories:create")
async def create_category(
        request: Request,
        parameters: Annotated[CreateCategoryParameters, Form()],
        connection=Depends(get_connection)):
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
    querier = Querier(connection)
    result = querier.delete_category(id=category_id)
    if result:
        return {"message": f"Category with ID {category_id} has been deleted successfully."}
    return HTTPException(status_code=404, detail=f"Category with ID {category_id} not found.")


@category_router.get("/", name="categories:index")
async def get_all_categories(request: Request, connection=Depends(get_connection)):
    querier = Querier(connection)
    categories = querier.get_all_categories()
    return templates.TemplateResponse(
        "categories/index.html", {"request": request, "categories": categories}
    )


@category_router.put("/{category_id}", name="categories:update")
async def update_category(
        request: Request,
        category_id: int,
        parameters: Annotated[CreateCategoryParameters, Form()],
        connection=Depends(get_connection)):
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
