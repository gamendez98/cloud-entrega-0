from datetime import timedelta, datetime, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM, LOGIN_URL


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



# OAuth2PasswordBearer will look for the token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=LOGIN_URL, auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str | RedirectResponse:
    if not token:
        raise HTTPException(status_code=307, headers={"Location": LOGIN_URL})
    check_blacklist(token)
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=307, headers={"Location": LOGIN_URL})
    username = payload.get("sub")
    return username


def get_current_token(token: str = Depends(oauth2_scheme)) -> str | RedirectResponse:
    check_blacklist(token)
    payload = verify_access_token(token)
    if payload is None:
        return RedirectResponse(url="/users/login", status_code=303)
    return token


def check_password(password_hash: str, entered_password: str):
    return bcrypt.checkpw(entered_password.encode('utf-8'), password_hash.encode('utf-8'))


def hash_password(password: str):
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )


blacklisted_tokens = set()


def black_list_token(token: str):
    blacklisted_tokens.add(token)


def check_blacklist(token: str):
    if token in blacklisted_tokens:
        raise HTTPException(status_code=401, detail="Token is blacklisted")
