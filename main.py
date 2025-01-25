from typing import Union

from fastapi import FastAPI

from endpoints.user import user_router

app = FastAPI()

app.include_router(user_router)
@app.get("/health-check")
def health_check():
    return {"status": "ok"}
