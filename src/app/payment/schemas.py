from pydantic import BaseModel,Field
from pydantic import EmailStr
from odmantic import ObjectId
from typing import Optional

class PaymentCreate(BaseModel):
    first_name:str
    last_name: str
    email :EmailStr
    amount : int
    project_id: str = Field(description="Project ID")
    
class PaymentIn(PaymentCreate):
    id: Optional[ObjectId] = None 
    reference: str = Field(description="Unique reference ID")
   

class PaymentUpdate(BaseModel):
    first_name:str
    last_name: str
    email :EmailStr
    amount : int
    project_id: str = Field(description="Project ID")

class PaymentIn(PaymentCreate):
    id: Optional[ObjectId] = None 
    reference: str = Field(description="Unique reference ID")