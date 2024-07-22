from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from datetime import datetime
from datetime import date
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from odmantic import ObjectId, Field
from typing import List,Optional

from app.db.base_class import Base

def datetime_now_sec():
    return datetime.now().replace(microsecond=0)

class Project(Base):
    name : str =Field(default = None, min_length =8)
    address: str=Field(default = None , min_length =8)
    zipcode : Optional[int] =Field(default =None, gt =5)
    created: Optional[datetime] = Field(default_factory=datetime_now_sec)
    modified: Optional[datetime] = Field(default_factory=datetime_now_sec)
    amount: int
    duration: datetime=Field(default_factory=datetime_now_sec)
    title: str =Field(default = None, min_length =8)
    about:Optional[str] =Field(default = None, min_length =8)
    picture_or_video:Optional[str] =Field(default=None)
    categories: str
    story:Optional[str]=Field(default =None)
    user_id : ObjectId