from fastapi import Response, Header, HTTPException
from sqlalchemy.orm.session import Session

from app.schemas import PaymentCreateResponse, PaymentCreateRequest
from datetime import datetime, timezone
from app.repository import payments as payments_repository
from app.database import SessionLocal

def get_payment(payment_id:str, db:Session):
    data = payments_repository.get_payment(db=db, payment_id=payment_id)
    if data:
        return data
    else:
        raise HTTPException(status_code=400, detail=f"There are no transactions with id {payment_id}")

def create_payment(db:Session, body:PaymentCreateRequest, idempotency_key:str=Header(..., max_length=50)):
    if info:=payments_repository.does_payment_exist(idempotency_key=idempotency_key, db=db):
        return {"message": "Payment already exists", "info": info}
    else:
        data = payments_repository.create_payment(db=db, body=body, idempotency_key=idempotency_key)
        return data

