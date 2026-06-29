from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict
from fastapi import HTTPException


class PaymentCreateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Сумма платежа")
    currency: str = Field(..., min_length=3, max_length=3, description="Валюта (RUB, USD, EUR)")
    description: Optional[str] = None
    meta: Dict = Field(default_factory=dict)
    webhook_url: str = Field(..., description="URL для webhook уведомлений")

    @field_validator("currency")
    def validate_currency(cls, v: str) -> str:
        allowed = {"RUB", "USD", "EUR"}
        if v not in allowed:
            raise HTTPException(status_code=400, detail=f"Currency must be one of {allowed}")
        return v.upper()


class PaymentCreateResponse(BaseModel):
    id: UUID
    status: str
    created_at: datetime


class PaymentResponse(BaseModel):
    id: UUID
    amount: Decimal
    currency: str
    description: Optional[str]
    meta: Dict
    status: str
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: Optional[datetime]


class WebhookPayload(BaseModel):
    payment_id: UUID
    status: str
    amount: Decimal
    currency: str
