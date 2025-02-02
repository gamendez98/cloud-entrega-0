from fastapi import FastAPI

from config import DEVELOPMENT
from endpoints.categories import category_router
from endpoints.tasks import tasks_router
from endpoints.users import user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your Vue frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(tasks_router)
app.include_router(category_router)


@app.get("/health-check")
def health_check():
    return {"status": "ok"}


if DEVELOPMENT:
    from fastapi.staticfiles import StaticFiles
    print("Starting server...")
    app.mount("/static", StaticFiles(directory="static"), name="static")
