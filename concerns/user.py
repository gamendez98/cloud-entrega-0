import os

from config import PROFILE_PICS_DIR
from models.models import Person


def get_profile_image_path(username: str, extension: str) -> str:
    file_name = f"{username}.{extension}"
    return os.path.join(PROFILE_PICS_DIR, file_name)