from typing import Optional , List
from typing_extensions import Annotated
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr,
    StringConstraints,
    field_validator,
    SecretStr,
    validator
)
from odmantic import ObjectId

from app.auth.exceptions import InvalidPasswordException
import re


class UserLogin(BaseModel):
    username: str
    password: str = Field(title = "password " , min_length = 8)
    
    @validator('password')
    def password_min_length(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return value


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    email_validated: Optional[bool] = False
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    niches: str = []
    full_name: str = ""
    location_id: Optional[ObjectId] = Field(None)


# Properties to receive via API on creation
class UserCreate(UserBase):
    verification_pin: str | None = None
    password: Optional[
        Annotated[str, StringConstraints(min_length=8, max_length=64)]
    ] = None

    @field_validator("password")
    @classmethod
    def regex_match(cls, p: str) -> str:
        re_for_pw: re.Pattern[str] = re.compile(
            r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]+$"
        )
        if not re_for_pw.match(p):
            raise InvalidPasswordException(
                "Password must contain at least one uppercase letter, one number, and one special character and be greater than 8 characters."
            )
        return p


# Properties to receive via API on update
class UserUpdate(UserBase):
    original: Optional[
        Annotated[str, StringConstraints(min_length=8, max_length=64)]
    ] = None
    password: Optional[
        Annotated[str, StringConstraints(min_length=8, max_length=64)]
    ] = None


class UserInDBBase(UserBase):
    id: Optional[ObjectId] = None
    model_config = ConfigDict(from_attributes=True)


# Additional properties to return via API
class User(UserInDBBase):
    hashed_password: bool = Field(default=False, alias="password")
    totp_secret: bool = Field(default=False, alias="totp")
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("hashed_password", mode="before")
    def evaluate_hashed_password(cls, hashed_password: str) -> bool:
        if hashed_password:
            return True
        return False

    @field_validator("totp_secret", mode="before")
    def evaluate_totp_secret(cls, totp_secret: str) -> bool:
        if totp_secret:
            return True
        return False


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: Optional[SecretStr] = None
    totp_secret: Optional[SecretStr] = None
    totp_counter: Optional[int] = None

class UserCreateReponse(BaseModel):
    status: int = 201
    message: str = "User Created Successfully"
    data: list = []

class NicheId(BaseModel):
    niches: List[str] = []
    
class NicheResponse(BaseModel):
    id : str
    name: str
    
class UserData(BaseModel):
    email: EmailStr
    email_validated: Optional[bool] = False
    niches: list[str] = []
    full_name: str = ""
    