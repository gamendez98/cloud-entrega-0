import shutil

from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from pydantic import BaseModel

from concerns.authentication import create_access_token, check_password, hash_password, get_current_user, \
    black_list_token, \
    get_current_token
from concerns.user import get_profile_image_path
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


class ImageResponse:
    def __init__(self, filename: str, file_path: str):
        self.filename = filename
        self.file_path = file_path


@user_router.post("/upload-image")
async def upload_image(file: UploadFile = File(...), connection=Depends(get_connection),
                       username: str = Depends(get_current_user)):
    # Generate a path for the uploaded file

    file_path = get_profile_image_path(username, file.filename.split(".")[-1])

    # Save the image file to the local filesystem
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Store the file path in the database
    querier = Querier(connection)
    querier.save_image_path(
        username=username,
        image_path=file_path,
    )
    connection.commit()

    # Return the filename and path where the image is saved
    return ImageResponse(filename=file.filename, file_path=file_path)


class Credentials(BaseModel):
    username: str
    password: str
    grant_type: str = "password"


@user_router.post("/login")
async def login(username: str = Form(...), password: str = Form(...), connection=Depends(get_connection)):
    querier = Querier(connection)
    password_hash = querier.get_password_hash(username=username)
    if not check_password(password_hash, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/logout")
async def logout(token=Depends(get_current_token)):
    black_list_token(token)
    return {"message": "Logged out successfully"}
