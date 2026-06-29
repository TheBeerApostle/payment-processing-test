from sqlalchemy import Column, String, Numeric, JSON, DateTime, Integer, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class OutboxStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    description = Column(String(255), nullable=True)
    meta = Column(JSON, nullable=False, default=dict)
    # Используем String вместо Enum для совместимости
    status = Column(String(20), nullable=False, default=PaymentStatus.PENDING.value)
    idempotency_key = Column(String(50), unique=True, nullable=False, index=True)
    webhook_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    processed_at = Column(DateTime, nullable=True)


class OutboxEvent(Base):
    __tablename__ = "outbox"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    # Используем String вместо Enum для совместимости
    status = Column(String(20), nullable=False, default=OutboxStatus.PENDING.value)
    retry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
