from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.schemas import PaymentCreateRequest, PaymentCreateResponse, PaymentResponse
from app.services.payments import PaymentService
from app.database import get_db
from app.dependency import verify_api_key

router = APIRouter()

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Получение информации о платеже"""
    service = PaymentService(db)
    return await service.get_payment(payment_id)

@router.post("", response_model=PaymentCreateResponse, status_code=202)
async def create_payment(
    body: PaymentCreateRequest,
    idempotency_key: str = Header(..., max_length=50),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Создание платежа"""
    service = PaymentService(db)
    return await service.create_payment(body, idempotency_key)