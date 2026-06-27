from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
class PaymentCreateRequest(BaseModel):
    amount: Decimal
    currency: str
    description: str | None
    meta: dict
    webhook_url: str
    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if not v>0:
            raise ValueError("Amount must be positive")

class PaymentCreateResponse(BaseModel):
    id: str
    status: str
    created_at: datetime