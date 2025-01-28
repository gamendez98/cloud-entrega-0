from typing import Union

from fastapi import FastAPI

from endpoints.categories import category_router
from endpoints.tasks import tasks_router
from endpoints.users import user_router

app = FastAPI()

app.include_router(user_router)
app.include_router(tasks_router)
app.include_router(category_router)


@app.get("/health-check")
def health_check():
    return {"status": "ok"}
