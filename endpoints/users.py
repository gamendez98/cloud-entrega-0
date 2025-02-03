import shutil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from concerns.authentication import create_access_token, check_password, hash_password, get_current_username, \
    black_list_token, \
    get_current_token, get_current_user
from concerns.user import get_profile_image_path
from config import templates, LOGIN_URL
from models.connection import get_connection
from models.users import Querier

user_router = APIRouter(prefix="/users", tags=["Users"])


class UserCreationParameters(BaseModel):
    username: str
    email: str
    password: str


@user_router.get("/", name="users:profile", response_class=HTMLResponse)
def get_user_profile(request: Request, user=Depends(get_current_user)):
    """
    Handles the retrieval of the user profile page.

    This function responds to the HTTP GET request for the user's profile page. It retrieves
    the user's data from the `get_current_user` dependency, ensures the user has a valid
    profile image path, and finally renders the user's profile page using the given
    template.

    :param request: The HTTP request object, providing data about the incoming request.
    :type request: Request
    :param user: The current user's data, provided by the get_current_user dependency.
    :type user: User
    :return: A rendered HTML response of the user's profile page.
    :rtype: HTMLResponse
    """
    if not user.image_path:
        user.image_path = "/static/resources/default.jpg"
    return templates.TemplateResponse(
        "users/profile.html", {"request": request, "user": user, "get_profile_image_path": get_profile_image_path}
    )


@user_router.get("/signin", name="users:signin", response_class=HTMLResponse)
async def signin_page(request: Request):
    """
    Handles rendering of the sign-in page for the application.

    This endpoint serves the HTML response for the user sign-in page, enabling
    users to access the authentication form.

    :param request: The HTTP request object received from the client.
    :type request: Request
    :return: A rendered HTML template response for the sign-in page.
    :rtype: TemplateResponse
    """
    return templates.TemplateResponse(
        'users/signin.html', {'request': request}
    )


@user_router.post("/signin", name="users:signin", response_class=RedirectResponse)
async def create_user(
        parameters: Annotated[UserCreationParameters, Form()],
        connection=Depends(get_connection)):
    """
    Handles the creation of a new user by processing form data, inserting the user
    record into the database, and redirecting the user to the login page after
    successful registration.

    :param parameters: Contains user creation details including username, email,
        and password, extracted from the form.
    :type parameters: UserCreationParameters
    :param connection: Database connection dependency instance provided by the
        dependency injection system.
    :return: A redirection response to the login URL with status code 303.
    :rtype: RedirectResponse
    """
    querier = Querier(connection)
    querier.create_user(
        username=parameters.username,
        email=parameters.email,
        password_hash=hash_password(parameters.password),
    )
    return RedirectResponse(url=LOGIN_URL, status_code=303)


class ImageResponse:
    def __init__(self, filename: str, file_path: str):
        self.filename = filename
        self.file_path = file_path


@user_router.post("/upload-image", name="users:upload_image", response_class=RedirectResponse)
async def upload_image(file: UploadFile = File(...), connection=Depends(get_connection),
                       username: str = Depends(get_current_username)):
    """
    Handles the upload of a user profile image by saving it to the filesystem and updating
    the database with the file path. It generates the destination path for the file based on
    the username and file extension. This endpoint redirects the user to the "/users" page
    after successfully uploading the image.

    :param file: An uploaded image file to be saved.
    :type file: UploadFile
    :param connection: A database connection dependency.
    :type connection: Depends
    :param username: The current username extracted via the authentication process.
    :type username: str
    :return: A redirect response to the "/users" page upon successful upload.
    :rtype: RedirectResponse
    """
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

    # Return the filename and path where the image is saved
    return RedirectResponse(url="/users", status_code=303)


class Credentials(BaseModel):
    username: str
    password: str
    grant_type: str = "password"


@user_router.get("/login", name="users:login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Handles the login page rendering and returns the appropriate HTML response.

    This function is responsible for rendering the login page for the users
    using the provided template and context. It is designed to return the
    HTMLResponse for the specified template, enriched with necessary request
    context data.

    :param request: The HTTP request object, which contains details about the
        incoming HTTP request such as headers, cookies, and query parameters.
        It also provides methods to access additional request information.
    :type request: Request
    :return: A TemplateResponse object generated from the 'users/login.html'
        template. This response contains the rendered HTML page along with
        the provided context for the request.
    :rtype: HTMLResponse
    """
    return templates.TemplateResponse(
        'users/login.html', {'request': request}
    )


@user_router.post("/login", response_class=RedirectResponse, name="users:login")
async def login(
        username: str = Form(...), password: str = Form(...), connection=Depends(get_connection)):
    """
    Handles user login by verifying credentials, generating an access token, and setting a cookie for
    authentication in subsequent requests. Redirects the user to the tasks page upon successful login.

    :param username: The username provided by the user during login.
    :type username: str
    :param password: The password provided by the user during login.
    :type password: str
    :param connection: The database connection dependency, used to query the user data.
    :type connection: Any
    :return: A RedirectResponse to the tasks page upon successful login.
    :rtype: RedirectResponse
    :raises HTTPException: Raised when the username or password is invalid, resulting in a 401 Unauthorized
        response status code.
    """
    querier = Querier(connection)
    password_hash = querier.get_password_hash(username=username)
    if not password_hash or not check_password(password_hash, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": username})

    response = RedirectResponse(
        url="/tasks",
        status_code=status.HTTP_303_SEE_OTHER
    )

    # Set cookie with specific domain and path
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True if using HTTPS
        samesite='lax',
        path='/',  # Important: Make cookie available for all paths
    )

    return response


@user_router.post("/logout", name="users:logout", response_class=RedirectResponse)
async def logout(token=Depends(get_current_token)):
    """
    Logs out the current user by invalidating and blacklisting the user's authentication
    token and redirects to the login page.

    :param token: The authentication token of the currently logged-in user, provided by
        `Depends(get_current_token)`.
    :return: A `RedirectResponse` object redirecting the user to the login page with an
        HTTP 303 status code.
    """
    black_list_token(token)
    return RedirectResponse(url=LOGIN_URL, status_code=303)
