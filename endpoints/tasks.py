from fastapi import APIRouter

tasks_router = APIRouter(prefix="/users", tags=["Tasks"])




@tasks_router.post("/")
async def create_task():
    return dict(
        message="Task created successfully."
    )