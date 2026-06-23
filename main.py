#TODO: заменить хардкод на БД
import uuid
from decimal import Decimal
from fastapi import FastAPI, Response, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime, timezone

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
app = FastAPI()

PROCESSED = ["example_key"]

class PaymentCreateRequest(BaseModel):
    amount: Decimal
    currency: str
    description: str | None
    meta: dict
    webhook_url: str

class PaymentCreateResponse(BaseModel):
    id: str
    status: str
    created_at: datetime

@app.get("/health")
def health_check():
    return Response(status_code=200)

@app.get("/api/v1/payments/{payment_id}")
def get_payment(payment_id:str):
    for payment in PAYMENTS:
        if payment["id"]==payment_id:
            return payment

@app.post("/api/v1/payments/")
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
        PROCESSED.append(idempotency_key)
        return PaymentCreateResponse.model_validate(new_payment)


