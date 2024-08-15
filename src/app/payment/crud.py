from typing import List, Optional, Any
from fastapi.exceptions import HTTPException
from motor.core import AgnosticDatabase
from odmantic import ObjectId
from app.project.models import Project
from app.db.base import CRUDBase
from app.user.models import User
from app.payment.models import  Payment
from app.project.models import Backers
from app.payment.schemas import PaymentCreate,PaymentUpdate
from app.config import settings



class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    
    async def get_all_payments(self, db: AgnosticDatabase) ->List[ Payment]:
        payment_collection =db.payment
        result = payment_collection.find()
        payments=[]
        async for document in result:
            document["id"]=str(document["_id"])
            del[document["_id"]]
            payments.append(Payment(**document))
        return payments
          
    async def save_payment(self, db: AgnosticDatabase, payment_data: Payment) -> Payment:
        payment_collection = db.payment
        payment = payment_data.dict()
        await payment_collection.insert_one(payment)
        return payment

    async def update_user_with_project(self,db:AgnosticDatabase, user_email: str, project_id: str):
        
        user_collection =db.user
        user = await user_collection.find_one({"email":user_email})
        if user:
            for projects in user["project_backed"]:
                if project_id != projects:
                    document ={"_id":ObjectId(user["_id"])}
                    update ={"$push":{"project_backed":ObjectId(project_id)}}
                    result = await user_collection.update_one(document,update)
                    
        return result.modified_count
            
    async def update_project_with_backer(self,db:AgnosticDatabase, project_id: str, user_email: str, amount: int):
        user_collection =db.user
        project_collection = db.project
        
        user =await user_collection.find_one({"email":user_email})
        project = await project_collection.find_one({"_id":ObjectId(project_id)})
        if project:
            
            document ={"_id":ObjectId(project_id)}
            backer =Backers(backer_name=user["full_name"], backer=user_email, amount =amount)
            backer =backer.dict()
            update = {"$push":{"backers":backer}}
            result = await project_collection.update_one(document,update)
        return result.modified_count
           
payment =CRUDPayment(Payment)