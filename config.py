import os

from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PROFILE_PICS_DIR = "static/profile_pics"
ENVIRONMENT = os.getenv("ENVIRONMENT")
DEVELOPMENT = True

templates = Jinja2Templates(directory="templates")

