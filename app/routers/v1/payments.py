from fastapi import FastAPI, Response, HTTPException, Header
from fastapi import APIRouter
from schemas import PaymentCreateResponse, PaymentCreateRequest
from repository.payments import
router = APIRouter()
@router.get("/{payment_id}")
def get_payment(payment_id:str):
    for payment in PAYMENTS:
        if payment["id"]==payment_id:
            return payment
    return None


@router.post("/")
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
        return Response(status_code=202, content=PaymentCreateResponse.model_validate(new_payment))