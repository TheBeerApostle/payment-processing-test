from fastapi import Header
from app.schemas import PaymentCreateResponse, PaymentCreateRequest
from app.repository.payments import PAYMENTS
from datetime import datetime, timezone


def create_payment(body:PaymentCreateRequest, idempotency_key:str)):
    if idempotency_key in PROCESSED:
        return f"Operation already exists."
    else:

        return PaymentCreateResponse.model_validate(new_payment)