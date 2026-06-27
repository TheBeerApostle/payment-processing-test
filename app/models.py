from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from decimal import Decimal
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transaction"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal]
    currency: Mapped[str]
    description: Mapped[str]
    metadata: Mapped[str]
    status: Mapped[str]
    idempotency_key: Mapped[str] = mapped_column(unique=True)
    webhook_url: Mapped[str]
    created_at: Mapped[datetime]
