from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from datetime import datetime
from datetime import date
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from odmantic import ObjectId, Field
from typing import List

from app.db.base_class import Base

def datetime_now_sec():
    return datetime.now().replace(microsecond=0)

class Project(Base):
    name : str
    address: str
    zipcode : int
    created: datetime = Field(default_factory=datetime_now_sec)
    modified: datetime = Field(default_factory=datetime_now_sec)
    amount: int
    duration: datetime=Field(default_factory=datetime_now_sec)
    Title: str
    about: str
    photo_or_video: str
    categories: str
    