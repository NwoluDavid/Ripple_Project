from pydantic import BaseModel,Field
from pydantic import EmailStr
from odmantic import ObjectId
from typing import Optional
from app.payment.models import Status

class PaymentCreate(BaseModel):
    first_name:str
    last_name: str
    email :EmailStr
    amount : int
    project_id: str = Field(description="Project ID")
    
class PaymentIn(PaymentCreate):
    id: Optional[ObjectId] = None 
    status: Status =Field(default =Status.pending,description="Payment Status")
    reference: str = Field(description="Unique reference ID")
    paid_at: str= Field(default = None, description="paid at is a date time str object")
   

class PaymentUpdate(BaseModel):
    first_name:str
    last_name: str
    email :EmailStr
    amount : int
    project_id: str = Field(description="Project ID")
    
class PaymentIn(PaymentCreate):
    id: Optional[ObjectId] = None 
    reference: str = Field(description="Unique reference ID")