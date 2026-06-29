# scripts/test_rabbitmq.py
# !/usr/bin/env python
"""
Скрипт для проверки RabbitMQ
Запуск: python scripts/test_rabbitmq.py
"""

import asyncio
import json
from app.rabbitmq import rabbitmq_client


async def test_rabbitmq():
    """Тест RabbitMQ"""
    print("Testing RabbitMQ connection...")

    # Подключаемся
    connected = await rabbitmq_client.connect()
    if connected:
        print("✅ Connected to RabbitMQ")
    else:
        print("❌ Failed to connect to RabbitMQ")
        return

    # Публикуем тестовое сообщение
    test_payload = {
        "payment_id": "test-123",
        "status": "pending",
        "amount": "100.00",
        "currency": "RUB"
    }

    success = await rabbitmq_client.publish_payment_created(
        payment_id="test-123",
        payload=test_payload
    )

    if success:
        print("✅ Test message published")
    else:
        print("❌ Failed to publish test message")

    # Закрываем соединение
    await rabbitmq_client.close()
    print("Connection closed")


if __name__ == "__main__":
    asyncio.run(test_rabbitmq())