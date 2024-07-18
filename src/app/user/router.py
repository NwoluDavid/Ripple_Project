from typing import Any , Annotated, List
from bson import ObjectId
import pprint

from fastapi import APIRouter, Body, Depends, HTTPException,Query
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from fastapi.responses import JSONResponse
from motor.core import AgnosticDatabase

from app.user import crud, schemas
from app.user import models
from app import deps
from app.config import settings
from app.auth import security
from app.auth.service import send_email_validation_email
from app.auth.schemas import EmailValidation 
from app.auth import deps as auth_deps
# from exceptions import BaseException


from app.user.deps import get_current_active_admin


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/",
    response_model=schemas.UserCreateReponse,
    description="Create or SignUp a new user",
)
async def create_user_profile(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    password: str = Body(
        ...,
        min_length=8,
        example="Password123!",
        description="Password must be exactly 8 characters long, contain at least one uppercase letter, one digit, and one special character.",
    ),
    email: EmailStr = Body(...),
) -> Any:
    """
    Create/SignUp new user without the need to be logged in.
    Note to sucessfully create a user the password must 
    be 8 characters and above.
    """
    try:
        user = await crud.user.get_by_email(db, email=email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="This email is not available.",
            )

        # Generate Verification Pin
        verification_pin = security.create_verification_pin()

        # Create user auth
        user_in = schemas.UserCreate(
            password=password, email=email, verification_pin=verification_pin
        )  # noqa

        email_data = EmailValidation(
            email=email, subject="Email Verification", token=verification_pin
        )  # noqa

        # send email verifiication to email
        if settings.EMAILS_ENABLED and email:
            send_email_validation_email(email_data)

        user = await crud.user.create(db, obj_in=user_in)

        return JSONResponse(
            status_code=201,
            content={
                "status": "Success",
                "message": "User created successfully",
                "data": [],
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "Error",
                "message": f"{e}",
                "data": None,
            },
        )


@router.get("/")
async def get_user(user:models.User = Depends(auth_deps.get_current_user)):
    
    """This route is to get the current user details"""
    
    try:
        user = user.dict()
        user = schemas.UserData(**user)
        user = jsonable_encoder(user)
        return JSONResponse(
                status_code=200,
                content={
                    "status": "Success",
                    "message": "User data retrived successfully",
                    "data": user,
                },
            )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "Error",
                "message": f"{e}",
                "data": None,
            },
        )
    


    