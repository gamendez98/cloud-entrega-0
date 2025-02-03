from datetime import timedelta, datetime, timezone

import bcrypt
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM, LOGIN_URL
from models.connection import get_connection
from models.users import Querier


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to verify the token
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_token(request: Request):
    token = request.cookies.get("access_token")
    return token


def get_current_username(token: str = Depends(get_token)) -> str | RedirectResponse:
    if not token:
        raise HTTPException(status_code=307, headers={"Location": LOGIN_URL})
    check_blacklist(token)
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=307, headers={"Location": LOGIN_URL})
    username = payload.get("sub")
    return username


def get_current_user(username: str = Depends(get_current_username), connection=Depends(get_connection)):
    querier = Querier(connection)
    return querier.get_user_by_username(username=username)


def get_current_token(token: str = Depends(get_token)) -> str | RedirectResponse:
    check_blacklist(token)
    payload = verify_access_token(token)
    if payload is None:
        return RedirectResponse(url="/users/login", status_code=303)
    return token


def check_password(password_hash: str, entered_password: str):
    return bcrypt.checkpw(entered_password.encode('utf-8'), password_hash.encode('utf-8'))


def hash_password(password: str):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password, salt)
    return password_hash.decode(
        'utf-8')


blacklisted_tokens = set()


def black_list_token(token: str):
    blacklisted_tokens.add(token)


def check_blacklist(token: str):
    if token in blacklisted_tokens:
        raise HTTPException(status_code=401, detail="Token is blacklisted")
