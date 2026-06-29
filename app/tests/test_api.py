
import requests
import uuid
import json

BASE_URL = "http://localhost:8001"  # Порт как в Docker
API_KEY = "test-api-key-12345"


def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Health check passed")


def test_create_payment():
    payload = {
        "amount": "100.50",
        "currency": "RUB",
        "description": "Test payment",
        "meta": {"order_id": "12345"},
        "webhook_url": "https://webhook.site/test"
    }
    headers = {
        "X-API-Key": API_KEY,
        "Idempotency-Key": f"test-{uuid.uuid4().hex[:8]}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/payments",
        json=payload,
        headers=headers
    )
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    print(f"✅ Payment created: {data['id']}")
    return data["id"]


def test_get_payment():
    payment_id = test_create_payment()
    headers = {"X-API-Key": API_KEY}
    response = requests.get(
        f"{BASE_URL}/api/v1/payments/{payment_id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == payment_id
    print("✅ Payment retrieved")


if __name__ == "__main__":
    test_health()
    test_create_payment()
    test_get_payment()
    print("\nAll tests passed!")