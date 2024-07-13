from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, SecretStr, EmailStr
from odmantic import Model, ObjectId


class RefreshTokenBase(BaseModel):
    token: SecretStr
    authenticates: Optional[Model] = None


class RefreshTokenCreate(RefreshTokenBase):
    authenticates: Model


class RefreshTokenUpdate(RefreshTokenBase):
    pass


class RefreshToken(RefreshTokenUpdate):
    pass
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[ObjectId] = None
    refresh: Optional[bool] = False
    totp: Optional[bool] = False


class MagicTokenPayload(BaseModel):
    sub: Optional[Any] = None
    fingerprint: Optional[str] = None


class WebToken(BaseModel):
    claim: str


class NewTOTP(BaseModel):
    secret: Optional[str] = None
    key: str
    uri: str


class EnableTOTP(BaseModel):
    claim: str
    uri: str
    password: Optional[str] = None


class EmailContent(BaseModel):
    email: EmailStr
    subject: str
    content: str


class EmailValidation(BaseModel):
    email: EmailStr
    subject: str
    token: str | int = int
