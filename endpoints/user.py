from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from authentication import create_access_token, check_password, hash_password
from models.connection import get_connection
from models.users import Querier

user_router = APIRouter(prefix="/users", tags=["Users"])


# Function to create an access token


class UserCreationParameters(BaseModel):
    username: str
    email: str
    password: str


@user_router.post("/")
async def create_user(parameters: UserCreationParameters, connection=Depends(get_connection)):
    querier = Querier(connection)
    querier.create_user(
        username=parameters.username,
        email=parameters.email,
        password_hash=hash_password(parameters.password),
    )
    connection.commit()
    return {"username": parameters.username, "email": parameters.email}


@user_router.post("/load-image")
async def load_image():
    # TODO
    pass


class Credentials(BaseModel):
    username: str
    password: str


@user_router.post("/login")
async def login(credentials: Credentials, connection=Depends(get_connection)):
    querier = Querier(connection)
    password_hash = querier.get_password_hash(username=credentials.username)
    if not check_password(password_hash, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": credentials.username})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/logout")
async def logout():
    # TODO
    pass

# TODO: get default image for user
