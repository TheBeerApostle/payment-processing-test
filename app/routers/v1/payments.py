from fastapi import Response, Header, Depends
from fastapi import APIRouter
from sqlalchemy.orm.session import Session

from app.schemas import PaymentCreateResponse, PaymentCreateRequest
import app.services.payments as payment_service
from dependency import db_connection
router = APIRouter()
@router.get("/{payment_id}")
def get_payment(payment_id:str, db:Session=Depends(db_connection)):
    return payment_service.get_payment(payment_id=payment_id, db=db)



@router.post("/")
def create_payment(body:PaymentCreateRequest, idempotency_key:str=Header(..., max_length=50), db:Session=Depends(db_connection)):
    return payment_service.create_payment(body=body,idempotency_key=idempotency_key, db=db)