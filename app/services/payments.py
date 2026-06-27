from fastapi import Response, Header
from fastapi import APIRouter
from app.schemas import PaymentCreateResponse, PaymentCreateRequest
from datetime import datetime, timezone
import uuid

PAYMENTS = [{
    "id": "28282",
    "amount": 200,
    "currency": "RUB",
    "description": None,
    "metadata": None,
    "status": "succeeded",
    "idempotency_key": "example_key",
    "webhook_url": "example.com",
    "created_at": "2024-01-01"
}]

PROCESSED = {"idempotency_key": "example_key", "info": PAYMENTS[0]}

def get_payment(payment_id:str):
    for payment in PAYMENTS:
        if payment["id"]==payment_id:
            return payment
    return None

def create_payment(body:PaymentCreateRequest, idempotency_key:str=Header(..., max_length=50)):
    if idempotency_key in PROCESSED:
        return f"Operation already exists."
    else:
        new_payment = {
            "id": str(uuid.uuid4()),
            "amount": body.amount,
            "currency": body.currency,
            "description": body.description,
            "metadata": body.meta,
            "status": "pending",
            "idempotency_key": idempotency_key,
            "webhook_url": body.webhook_url,
            "created_at": datetime.now(timezone.utc)
        }
        PAYMENTS.append(new_payment)
        PROCESSED[idempotency_key] = new_payment
        return PaymentCreateResponse.model_validate(new_payment)