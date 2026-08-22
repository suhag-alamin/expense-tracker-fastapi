from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oAuth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")
# secret key jwt from .env file
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_access_token(username: str, user_id: int, expires_delta: timedelta = timedelta(minutes=30)):
    encode = {
        "sub": username,
        "id": user_id,
    }
    expires = datetime.now(
        timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=30))
    encode.update({
        "exp": expires
    })
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=401, detail="Invalid token or expired token")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid token or expired token")
