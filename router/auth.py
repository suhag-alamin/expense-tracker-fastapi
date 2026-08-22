from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from datetime import timedelta, datetime
from models import User
from dependencies import db_dependency
from security import bcrypt_context, create_access_token

router = APIRouter()


class CreateUser(BaseModel):
    username: str = Field(..., examples=["john_doe"])
    email: str = Field(..., examples=["john.doe@example.com"])
    password: str = Field(..., examples=["password123"])


# authenticate user
def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.post("/register")
def register_user(user: CreateUser, db: db_dependency):
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password)

    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(content={"message": "User registered successfully!"}, status_code=201)


@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")
    else:
        access_token_expires = timedelta(minutes=15)
        access_token = create_access_token(
            user.username, user.id, access_token_expires
        )
        return JSONResponse(content={
            "message": "Login successful!",
            "access_token": access_token,
            "token_type": "bearer"
        },
            status_code=200
        )
