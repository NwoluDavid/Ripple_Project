from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from motor.core import AgnosticDatabase
import pprint

from app.auth import schemas
from app.user import models
from app.user import crud as user_crud
from app.auth import crud as auth_crud
from app.config import settings
from app.deps import get_db

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/oauth")


def get_token_payload(token: str) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return token_data


async def get_current_user(
    db: AgnosticDatabase = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    token_data = get_token_payload(token)
    if token_data.refresh or token_data.totp:
        # Refresh token is not a valid access token and TOTP True can only be used to validate TOTP
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await user_crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_magic_token(token: str = Depends(reusable_oauth2)) -> schemas.MagicTokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.MagicTokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials - {e}",
        )
    return token_data


async def get_refresh_user(
    db: AgnosticDatabase = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User | None:
    token_data = get_token_payload(token)
    if not token_data.refresh:
        # Access token is not a valid refresh token
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await user_crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user_crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    # Check and revoke this refresh token
    token_obj = await auth_crud.token.get(token=token, user=user)
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    await auth_crud.token.remove(db, db_obj=token_obj)

    # Make sure to revoke all other refresh tokens
    return await user_crud.user.get(db=db, id=token_data.sub)


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not user_crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not user_crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_active_websocket_user(*, db: AgnosticDatabase, token: str) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO])
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise ValidationError("Could not validate credentials")
    if token_data.refresh:
        # Refresh token is not a valid access token
        raise ValidationError("Could not validate credentials")
    user = await user_crud.user.get(db, id=token_data.sub)
    if not user:
        raise ValidationError("User not found")
    if not user_crud.user.is_active(user):
        raise ValidationError("Inactive user")
    return user
