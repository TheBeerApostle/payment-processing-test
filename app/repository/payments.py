from app.models import Transaction






PAYMENTS = [{
    "id": "28282",
    "amount": 200,
    "currency": "RUB",
    "description": None,
    "metadata": None,
    "status": "succeeded",
    "idempotency_key": "example_key",
    "webhook_url": "example.com",
    "created_at": "2024-01-01"
}]

def add_payment(body:):
    new_payment = {
        "id": int(uuid.uuid4()),
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

