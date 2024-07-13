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



