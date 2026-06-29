# scripts/check_queues.py
# !/usr/bin/env python
"""
Скрипт для проверки состояния очередей RabbitMQ
Запуск: python scripts/check_queues.py
"""

import asyncio
from app.rabbitmq import rabbitmq_client


async def check_queues():
    """Проверка очередей"""
    print("Checking RabbitMQ queues...")

    await rabbitmq_client.connect()

    # Получаем информацию об очередях
    channel = rabbitmq_client.channel

    # Проверяем основную очередь
    queue = await channel.get_queue("payments.new")
    queue_info = await queue.declare()

    print(f"\nQueue: payments.new")
    print(f"  - Messages ready: {queue_info.message_count}")
    print(f"  - Consumers: {queue_info.consumer_count}")

    # Проверяем DLQ
    dlq = await channel.get_queue("payments.dlq.queue")
    dlq_info = await dlq.declare()

    print(f"\nQueue: payments.dlq.queue")
    print(f"  - Messages ready: {dlq_info.message_count}")
    print(f"  - Consumers: {dlq_info.consumer_count}")

    await rabbitmq_client.close()


if __name__ == "__main__":
    asyncio.run(check_queues())