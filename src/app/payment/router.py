from fastapi import APIRouter, HTTPException, Request,Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from motor.core import AgnosticDatabase
import requests
from app.config import settings
import hmac
import hashlib
import json
from app.auth.deps import get_current_active_superuser,get_current_user
from app.payment.schemas import PaymentCreate
from app.payment.models import Payment
from app.user.models import User
from app.deps import get_db
from app.payment.crud import payment
import uuid
import pprint


router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)

@router.get("/" , response_model =Payment)
async def get_payments(
    user:User =Depends(get_current_active_superuser),
    db:AgnosticDatabase =Depends(get_db)
):
    try:
        payments_data =await payment.get_all_payments(db)
        payments_data =jsonable_encoder(payments_data)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "payments data retrived successfully",
            "data": payments_data
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        }) 


@router.post("/initialize-payment/")
async def initialize_payment(paymentin: PaymentCreate,user:User=Depends(get_current_user) ,db:AgnosticDatabase=Depends(get_db)):
    try:
        if user.email !=paymentin.email:
            raise HTTPException(status_code =400 , detail="this user is not registered")
        
        unique_reference = f"{paymentin.project_id}-{uuid.uuid4()}"
        
        url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "first_name":paymentin.first_name,
            "last_name":paymentin.last_name,
            "email": paymentin.email,
            "amount": paymentin.amount * 100 , # Amount in kobo
            "reference": unique_reference
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Payment initialization failed")
        
        # Save the payment initialization data
        payment_data =Payment(
            first_name=paymentin.first_name,
            last_name =paymentin.last_name,
            email= paymentin.email,
            amount= paymentin.amount,
            reference= unique_reference,
            project_id= paymentin.project_id
        )
        
        await payment.save_payment(db, payment_data)
        
        return response.json()  # The response contains the authorization URL

    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        }) 


@router.get("/verify-transaction/{reference}")
async def verify_transaction(reference: str , db:AgnosticDatabase=Depends(get_db)):
    try:
        url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Transaction verification failed")
        
        event = response.json()
        transaction_reference = event['data']['reference']
        status=event['data']["status"]
        paid_at=event['data']["paid_at"]
        if event['data']["status"] =="success":
            # transaction_reference = event['data']['reference']
            # status=event['data']["status"]
            # user_email = event['data']['customer']['email']
            # amount = event['data']['amount'] // 100  # Amount is in kobo
            
            # Extract project ID from reference
            # project_id = transaction_reference.split('-')[0]
            # await payment.update_user_with_project(db, user_email, project_id)
            # await payment.update_project_with_backer(db, project_id, user_email, amount)
            await payment.update_payment_status(db,transaction_reference,status,paid_at)
            return {"status": "success"}
        else:
            await payment.update_payment_status(db,transaction_reference,status,paid_at)
            raise HTTPException(status_code=400, detail ="this transaction was not successful")
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        }) 
        

@router.post("/webhook/")
async def paystack_webhook(request: Request, db: AgnosticDatabase = Depends(get_db)):
    try:
        payload = await request.body()
        signature = request.headers.get("x-paystack-signature")
        
        # Verify the webhook signature
        expected_signature = hmac.new(
            bytes(settings.PAYSTACK_SECRET_KEY, 'utf-8'),
            msg=payload,
            digestmod=hashlib.sha512
        ).hexdigest()
        
        if signature != expected_signature:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        event = json.loads(payload)
        transaction_reference = event['data']['reference']
        status=event['data']["status"]
        paid_at=event['data']["paid_at"]
        if event['event'] == 'charge.success':
            user_email = event['data']['customer']['email']
            amount = event['data']['amount'] // 100  # Amount is in kobo
            
            # Extract project ID from reference
            project_id = transaction_reference.split('-')[0]
            
            await payment.update_user_with_project(db, user_email, project_id)
            await payment.update_project_with_backer(db, project_id, user_email, amount)
            await payment.update_payment_status(db,transaction_reference,status,paid_at)
            return {"status": "success"}
        else:
            await payment.update_payment_status(db,transaction_reference,status,paid_at)
            raise HTTPException(status_code=400, detail ="this transaction was not successful")
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        }) 