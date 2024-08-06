from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from datetime import datetime
from datetime import date
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from odmantic import ObjectId, Field
from typing import List,Optional

from app.db.base_class import Base


class Payment(Base):
    email: EmailStr
    amount: int
    reference: str = Field(description="Unique reference ID")
    project_id: str = Field(description="Project ID")