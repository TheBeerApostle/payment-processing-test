import pytest
from httpx import AsyncClient
import uuid


class TestPaymentAPI:

    @pytest.mark.asyncio
    async def test_create_payment_success(self, client: AsyncClient, api_key: str, idempotency_key: str):
        """Тест успешного создания платежа"""
        response = await client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": api_key,
                "Idempotency-Key": idempotency_key,
                "Content-Type": "application/json"
            },
            json={
                "amount": "100.50",
                "currency": "RUB",
                "description": "Test payment",
                "meta": {"order_id": "12345"},
                "webhook_url": "https://webhook.site/test"
            }
        )

        assert response.status_code == 202
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_payment_idempotency(self, client: AsyncClient, api_key: str):
        """Тест идемпотентности - одинаковый Idempotency-Key"""
        idempotency_key = str(uuid.uuid4())

        # Первый запрос
        response1 = await client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": api_key,
                "Idempotency-Key": idempotency_key,
                "Content-Type": "application/json"
            },
            json={
                "amount": "200.00",
                "currency": "USD",
                "description": "Test idempotency",
                "meta": {},
                "webhook_url": "https://webhook.site/test"
            }
        )

        # Второй запрос с тем же ключом
        response2 = await client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": api_key,
                "Idempotency-Key": idempotency_key,
                "Content-Type": "application/json"
            },
            json={
                "amount": "300.00",  # Другая сумма
                "currency": "EUR",
                "description": "Different description",
                "meta": {},
                "webhook_url": "https://webhook.site/test"
            }
        )

        # Должны вернуть одинаковые результаты
        assert response1.status_code == 202
        assert response2.status_code == 202
        assert response1.json()["id"] == response2.json()["id"]

    @pytest.mark.asyncio
    async def test_get_payment(self, client: AsyncClient, api_key: str, idempotency_key: str):
        """Тест получения платежа"""
        # Сначала создаем платеж
        create_response = await client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": api_key,
                "Idempotency-Key": idempotency_key,
                "Content-Type": "application/json"
            },
            json={
                "amount": "150.75",
                "currency": "RUB",
                "description": "Test get",
                "meta": {"test": True},
                "webhook_url": "https://webhook.site/test"
            }
        )

        payment_id = create_response.json()["id"]

        # Получаем платеж
        get_response = await client.get(
            f"/api/v1/payments/{payment_id}",
            headers={"X-API-Key": api_key}
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == payment_id
        assert data["amount"] == "150.75"
        assert data["currency"] == "RUB"

    @pytest.mark.asyncio
    async def test_get_payment_not_found(self, client: AsyncClient, api_key: str):
        """Тест получения несуществующего платежа"""
        import uuid
        fake_id = uuid.uuid4()

        response = await client.get(
            f"/api/v1/payments/{fake_id}",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_api_key(self, client: AsyncClient):
        """Тест с невалидным API ключом"""
        response = await client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": "invalid-key",
                "Idempotency-Key": "test",
                "Content-Type": "application/json"
            },
            json={
                "amount": "100.00",
                "currency": "RUB",
                "description": "Test",
                "meta": {},
                "webhook_url": "https://webhook.site/test"
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_currency(self, client: AsyncClient, api_key: str, idempotency_key: str):
        """Тест с невалидной валютой"""
        response = await client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": api_key,
                "Idempotency-Key": idempotency_key,
                "Content-Type": "application/json"
            },
            json={
                "amount": "100.00",
                "currency": "XXX",  # Невалидная валюта
                "description": "Test",
                "meta": {},
                "webhook_url": "https://webhook.site/test"
            }
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_negative_amount(self, client: AsyncClient, api_key: str, idempotency_key: str):
        """Тест с отрицательной суммой"""
        response = await client.post(
            "/api/v1/payments",
            headers={
                "X-API-Key": api_key,
                "Idempotency-Key": idempotency_key,
                "Content-Type": "application/json"
            },
            json={
                "amount": "-100.00",  # Отрицательная сумма
                "currency": "RUB",
                "description": "Test",
                "meta": {},
                "webhook_url": "https://webhook.site/test"
            }
        )

        assert response.status_code == 400