
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.payments import PaymentRepository
from app.schemas import PaymentCreateRequest, PaymentCreateResponse, PaymentResponse
from uuid import UUID

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.repository = PaymentRepository(db)

    async def get_payment(self, payment_id: UUID) -> PaymentResponse:
        payment = await self.repository.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        return PaymentResponse.model_validate(payment)

    async def create_payment(self, request: PaymentCreateRequest, idempotency_key: str) -> PaymentCreateResponse:
        existing = await self.repository.get_by_idempotency_key(idempotency_key)
        if existing:
            return PaymentCreateResponse(
                id=existing.id,
                status=existing.status,  # status теперь строка, не .value
                created_at=existing.created_at
            )

        try:
            payment, outbox_event = await self.repository.create(request, idempotency_key)
            return PaymentCreateResponse(
                id=payment.id,
                status=payment.status,  # status теперь строка, не .value
                created_at=payment.created_at
            )
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))