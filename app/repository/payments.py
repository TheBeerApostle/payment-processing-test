import uuid
from datetime import datetime, timezone
from fastapi import Header
from sqlalchemy.orm import Session
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


def does_payment_exist(db: Session, idempotency_key: str = Header(..., max_length=50)):
    payment = db.query(Transaction).filter(Transaction.idempotency_key == idempotency_key).first()
    return payment


def get_payment(db: Session, payment_id: str):
    payment = db.query(Transaction).filter(Transaction.id == payment_id).first()
    return payment


def create_payment(db: Session, body: PaymentCreateRequest, idempotency_key: str = Header(..., max_length=50)):
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
    payment = Transaction(**new_payment)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
