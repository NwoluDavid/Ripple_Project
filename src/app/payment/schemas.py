from pydantic import BaseModel,Field
from pydantic import EmailStr
from odmantic import ObjectId
from typing import Optional

class PaymentCreate(BaseModel):
    email :EmailStr
    amount : int
    reference: str =Field(default = None , description= "project id")
    
class PaymentIn(PaymentCreate):
   id: Optional[ObjectId] = None 
   

class PaymentUpdate(BaseModel):
    email :EmailStr
    amount : int
    reference: str =Field(default = None , description= "project id")

class PaymentUp(PaymentUpdate):
    id: Optional[ObjectId] = None 