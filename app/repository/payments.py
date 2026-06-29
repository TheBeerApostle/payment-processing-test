import uuid
from datetime import datetime, timezone

from fastapi import Header

from app.models import Transaction
from app.schemas import PaymentCreateRequest, PaymentCreateResponse

PAYMENTS = [{
    "id": "28282",
    "amount": 200,
    "currency": "RUB",
    "description": None,
    "meta": None,
    "status": "succeeded",
    "idempotency_key": "example_key",
    "webhook_url": "example.com",
    "created_at": "2024-01-01"
}]

PROCESSED = [{"idempotency_key": "example_key", "info": PAYMENTS[0]}]

def does_payment_exist(idempotency_key:str=Header(..., max_length=50)):
    for i in PROCESSED:
        if i["idempotency_key"] == idempotency_key:
            return i["info"]
    return False

def get_payment(payment_id:str):
    for payment in PAYMENTS:
        if payment["id"]==payment_id:
            return payment
    return None

def create_payment(body:PaymentCreateRequest, idempotency_key:str=Header(..., max_length=50)):
    new_payment = {
        "id": str(uuid.uuid4()),
        "amount": body.amount,
        "currency": body.currency,
        "description": body.description,
        "meta": body.meta,
        "status": "pending",
        "idempotency_key": idempotency_key,
        "webhook_url": body.webhook_url,
        "created_at": datetime.now(timezone.utc)
    }
    PAYMENTS.append(new_payment)
    PROCESSED.append({"idempotency_key": idempotency_key, "info": new_payment})
    return PaymentCreateResponse.model_validate(new_payment)





