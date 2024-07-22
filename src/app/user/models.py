from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from datetime import datetime
from datetime import date
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from odmantic import ObjectId, Field
from typing import List

from app.db.base_class import Base

if TYPE_CHECKING:
    from . import Token  # noqa: F401


def datetime_now_sec():
    return datetime.now().replace(microsecond=0)



class User(Base):
    created: datetime = Field(default_factory=datetime_now_sec)
    modified: datetime = Field(default_factory=datetime_now_sec)
    full_name: str = Field(default="")
    email: EmailStr
    phone: Optional[PhoneNumber] = Field(default = None, description="user phone number")
    date_of_birth:Optional[datetime] =Field(default_factory=datetime_now_sec)
    address: Optional[str]= Field(default=None)
    hashed_password: Any = Field(default=None)
    totp_secret: Any = Field(default=None)
    totp_counter: Optional[int] = Field(default=None)
    email_validated: bool = Field(default=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=True)
    refresh_tokens: list[ObjectId] = Field(default_factory=list)
    verification_pin: str = Field(default=None)

