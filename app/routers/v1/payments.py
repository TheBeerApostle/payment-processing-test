from fastapi import Response, Header
from fastapi import APIRouter
from app.schemas import PaymentCreateResponse, PaymentCreateRequest
import app.services.payments as payment_service
from datetime import datetime, timezone
import uuid
router = APIRouter()
@router.get("/{payment_id}")
def get_payment(payment_id:str):
    return payment_service.get_payment(payment_id=payment_id)



@router.post("/")
def create_payment(body:PaymentCreateRequest, idempotency_key:str=Header(..., max_length=50)):
    return payment_service.create_payment(body=body,idempotency_key=idempotency_key)