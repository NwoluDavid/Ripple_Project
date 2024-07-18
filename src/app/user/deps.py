
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from motor.core import AgnosticDatabase

from app.auth import schemas
from app.user import models
from app.user import crud as user_crud
from app.auth import crud as auth_crud
from app.config import settings
from app.deps import get_db



from fastapi import Depends
from app.auth.deps import get_current_active_user
from app.user.models import User

def get_current_active_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can access this endpoint")
    return current_user
