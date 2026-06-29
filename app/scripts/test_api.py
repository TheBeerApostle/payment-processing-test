#!/usr/bin/env python
"""
Скрипт для ручного тестирования API
Запуск: python scripts/test_api.py
"""

import requests
import uuid
import json
import sys
import os

# Добавляем корневую папку в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

BASE_URL = "http://localhost:8000"
API_KEY = settings.API_KEY


def test_create_payment():
    """Тест создания платежа"""
    print("\n=== Тест создания платежа ===")

    idempotency_key = str(uuid.uuid4())

    response = requests.post(
        f"{BASE_URL}/api/v1/payments",
        headers={
            "X-API-Key": API_KEY,
            "Idempotency-Key": idempotency_key,
            "Content-Type": "application/json"
        },
        json={
            "amount": "100.50",
            "currency": "RUB",
            "description": "Test payment from script",
            "meta": {
                "order_id": "12345",
                "user_id": "user_123"
            },
            "webhook_url": "https://webhook.site/your-webhook-id"
        }
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 202:
        return response.json()["id"]
    return None


def test_get_payment(payment_id):
    """Тест получения платежа"""
    print(f"\n=== Тест получения платежа {payment_id} ===")

    response = requests.get(
        f"{BASE_URL}/api/v1/payments/{payment_id}",
        headers={"X-API-Key": API_KEY}
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response


def test_idempotency():
    """Тест идемпотентности"""
    print("\n=== Тест идемпотентности ===")

    idempotency_key = str(uuid.uuid4())

    # Первый запрос
    response1 = requests.post(
        f"{BASE_URL}/api/v1/payments",
        headers={
            "X-API-Key": API_KEY,
            "Idempotency-Key": idempotency_key,
            "Content-Type": "application/json"
        },
        json={
            "amount": "200.00",
            "currency": "USD",
            "description": "First request",
            "meta": {},
            "webhook_url": "https://webhook.site/test"
        }
    )

    print(f"First request status: {response1.status_code}")
    print(f"First request ID: {response1.json().get('id')}")

    # Второй запрос с тем же ключом
    response2 = requests.post(
        f"{BASE_URL}/api/v1/payments",
        headers={
            "X-API-Key": API_KEY,
            "Idempotency-Key": idempotency_key,
            "Content-Type": "application/json"
        },
        json={
            "amount": "999.99",  # Другая сумма
            "currency": "EUR",
            "description": "Second request (should be ignored)",
            "meta": {},
            "webhook_url": "https://webhook.site/test"
        }
    )

    print(f"Second request status: {response2.status_code}")
    print(f"Second request ID: {response2.json().get('id')}")

    # Проверяем что ID одинаковые
    if response1.json().get('id') == response2.json().get('id'):
        print("✅ Идемпотентность работает: ID одинаковые")
    else:
        print("❌ Идемпотентность НЕ работает: ID разные")


def test_errors():
    """Тест обработки ошибок"""
    print("\n=== Тест обработки ошибок ===")

    # Невалидный API ключ
    response = requests.post(
        f"{BASE_URL}/api/v1/payments",
        headers={
            "X-API-Key": "invalid-key",
            "Idempotency-Key": str(uuid.uuid4()),
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
    print(f"Invalid API key: {response.status_code} (should be 401)")

    # Невалидная валюта
    response = requests.post(
        f"{BASE_URL}/api/v1/payments",
        headers={
            "X-API-Key": API_KEY,
            "Idempotency-Key": str(uuid.uuid4()),
            "Content-Type": "application/json"
        },
        json={
            "amount": "100.00",
            "currency": "XXX",
            "description": "Test",
            "meta": {},
            "webhook_url": "https://webhook.site/test"
        }
    )
    print(f"Invalid currency: {response.status_code} (should be 400)")

    # Отрицательная сумма
    response = requests.post(
        f"{BASE_URL}/api/v1/payments",
        headers={
            "X-API-Key": API_KEY,
            "Idempotency-Key": str(uuid.uuid4()),
            "Content-Type": "application/json"
        },
        json={
            "amount": "-100.00",
            "currency": "RUB",
            "description": "Test",
            "meta": {},
            "webhook_url": "https://webhook.site/test"
        }
    )
    print(f"Negative amount: {response.status_code} (should be 400)")


def main():
    """Основная функция"""
    print("=" * 50)
    print("Тестирование Payment API")
    print("=" * 50)
    print(f"API URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    print("=" * 50)

    # Проверяем доступность сервера
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Сервер недоступен. Запустите сервер командой: uvicorn app.main:app --reload")
            return
        print("✅ Сервер доступен")
    except requests.exceptions.ConnectionError:
        print("❌ Сервер недоступен. Запустите сервер командой: uvicorn app.main:app --reload")
        return

    # Запускаем тесты
    test_errors()
    test_idempotency()

    payment_id = test_create_payment()
    if payment_id:
        test_get_payment(payment_id)

    print("\n" + "=" * 50)
    print("Тестирование завершено!")
    print("=" * 50)


if __name__ == "__main__":
    main()