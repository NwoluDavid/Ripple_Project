from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from datetime import datetime
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from odmantic import ObjectId, Field
from typing import List,Optional
from enum import Enum

from app.db.base_class import Base

def datetime_now_sec():
    return datetime.now().replace(microsecond=0)

class Status(str,Enum):
    pending ="Pending"
    success ="Success"
    failed ="Failed"

class Payment(Base):
    created: Optional[datetime] = Field(default_factory=datetime_now_sec)
    paid_at: str
    first_name:str
    last_name: str
    email: EmailStr
    amount: int
    date:str
    reference: str = Field(description="Unique reference ID")
    project_id: str = Field(description="Project ID",max_length =24)
    status: Status = Field(default =Status.pending,description="Payment Status")