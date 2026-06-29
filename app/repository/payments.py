import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models import Payment, PaymentStatus, OutboxEvent, OutboxStatus
from app.schemas import PaymentCreateRequest
from uuid import UUID


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, key: str) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(Payment.idempotency_key == key)
        )
        return result.scalar_one_or_none()

    async def create(self, request: PaymentCreateRequest, idempotency_key: str) -> tuple[Payment, OutboxEvent]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        payment = Payment(
            id=uuid.uuid4(),
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            meta=request.meta,
            webhook_url=request.webhook_url,
            idempotency_key=idempotency_key,
            status=PaymentStatus.PENDING.value,
            created_at=now
        )

        outbox_event = OutboxEvent(
            id=uuid.uuid4(),
            aggregate_id=payment.id,
            event_type="payment.created",
            payload={
                "payment_id": str(payment.id),
                "amount": str(payment.amount),
                "currency": payment.currency,
                "webhook_url": payment.webhook_url,
                "status": payment.status
            },
            status=OutboxStatus.PENDING.value,
            retry_count=0,
            created_at=now
        )

        self.db.add(payment)
        self.db.add(outbox_event)

        try:
            await self.db.commit()
            await self.db.refresh(payment)
            await self.db.refresh(outbox_event)
            return payment, outbox_event
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Duplicate idempotency key")

    async def update_status(self, payment_id: UUID, status: PaymentStatus) -> Payment | None:
        payment = await self.get_by_id(payment_id)
        if payment:
            payment.status = status.value
            payment.processed_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.commit()
            await self.db.refresh(payment)
        return payment

    async def get_pending_outbox_events(self, limit: int = 10) -> list[OutboxEvent]:
        result = await self.db.execute(
            select(OutboxEvent)
            .where(OutboxEvent.status == OutboxStatus.PENDING.value)
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_outbox_processed(self, event_id: UUID) -> None:
        event = await self.db.get(OutboxEvent, event_id)
        if event:
            event.status = OutboxStatus.PROCESSED.value
            event.processed_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.commit()

    async def mark_outbox_failed(self, event_id: UUID, error: str) -> None:
        event = await self.db.get(OutboxEvent, event_id)
        if event:
            event.status = OutboxStatus.FAILED.value
            event.error_message = error
            event.processed_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.commit()

