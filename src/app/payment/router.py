from fastapi import APIRouter, HTTPException, Request,Depends
from pydantic import BaseModel
from motor.core import AgnosticDatabase
import requests
from app.config import settings
import hmac
import hashlib
import json
from app.payment.schemas import PaymentCreate
from app.payment.models import Payment
from app.deps import get_db
from app.payment.crud import payment

router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)



@router.post("/initialize-payment/")
async def initialize_payment(payment: PaymentCreate):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": payment.email,
        "amount": payment.amount * 100 , # Amount in kobo
        "reference":payment.reference
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Payment initialization failed")
    return response.json()  # The response contains the authorization URL

@router.get("/verify-transaction/{reference}")
async def verify_transaction(reference: str):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Transaction verification failed")
    
    return response.json()

@router.post("/webhook/")
async def paystack_webhook(request: Request, db: AgnosticDatabase = Depends(get_db)):
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
    
    if event['event'] == 'charge.success':
        transaction_reference = event['data']['reference']
        user_email = event['data']['customer']['email']
        amount = event['data']['amount'] // 100  # Amount is in kobo
        
        # Save the payment transaction
        payment_data = {
            "email": user_email,
            "amount": amount,
            "reference": transaction_reference
        }
        await payment.save_payment(db, payment_data)
        
        # Update user with project id
        await payment.update_user_with_project(db, user_email, transaction_reference)
        
        # Update project with backer info
        await payment.update_project_with_backer(db, transaction_reference, user_email, amount)
        
        return {"status": "success"}
    
    return {"status": "ignored"}