from fastapi import APIRouter

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/")
async def create_user():
    # TODO
    pass

@user_router.post("/load-image")
async def load_image():
    # TODO
    pass


@user_router.post("/login")
async def login():
    # TODO
    pass

@user_router.get("/logout")
async def logout():
    # TODO
    pass

# TODO: get default image for user

