from pydantic import BaseModel, Field
from decimal import Decimal
class PaymentCreateRequest(BaseModel):
    amount: Decimal
    currency: str
    description: str | None
    meta: dict
    webhook_url: str

class PaymentCreateResponse(BaseModel):
    id: str
    status: str
    created_at: datetime