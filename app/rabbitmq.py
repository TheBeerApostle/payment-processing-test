import aio_pika
from aio_pika import Message, connect_robust, ExchangeType
from app.config import settings
import json
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None

        self.PAYMENTS_EXCHANGE = "payments"
        self.PAYMENTS_QUEUE = "payments.new"
        self.DLQ_QUEUE = "payments.dlq.queue"
        self.DEAD_LETTER_EXCHANGE = "payments.dlx"

    async def connect(self):
        try:
            self.connection = await connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()

            # Объявляем обменники
            self.exchange = await self.channel.declare_exchange(
                self.PAYMENTS_EXCHANGE,
                ExchangeType.DIRECT,
                durable=True
            )

            dlx = await self.channel.declare_exchange(
                self.DEAD_LETTER_EXCHANGE,
                ExchangeType.DIRECT,
                durable=True
            )

            # Основная очередь с DLX
            queue = await self.channel.declare_queue(
                self.PAYMENTS_QUEUE,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": self.DEAD_LETTER_EXCHANGE,
                    "x-dead-letter-routing-key": self.DLQ_QUEUE
                }
            )

            # DLQ очередь
            dlq = await self.channel.declare_queue(
                self.DLQ_QUEUE,
                durable=True
            )

            # Привязываем очереди к обменникам
            await queue.bind(self.exchange, routing_key="payment.created")
            await dlq.bind(dlx, routing_key=self.DLQ_QUEUE)

            logger.info("RabbitMQ connected and exchanges/queues declared")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False

    async def publish_payment_created(self, payment_id: str, payload: dict) -> bool:
        try:
            if not self.channel:
                await self.connect()

            message = Message(
                body=json.dumps({
                    "payment_id": payment_id,
                    "payload": payload,
                    "event_type": "payment.created"
                }).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await self.exchange.publish(
                message,
                routing_key="payment.created"
            )

            logger.info(f"Published payment.created event for {payment_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    async def consume_payments(self, callback: Callable):
        """Потребление сообщений из очереди"""
        try:
            if not self.channel:
                await self.connect()

            queue = await self.channel.get_queue(self.PAYMENTS_QUEUE)

            # Используем итератор без автоматического подтверждения
            async with queue.iterator(no_ack=False) as queue_iter:
                async for message in queue_iter:
                    try:
                        # Передаем сообщение в callback
                        await callback(message)
                        # callback сам подтверждает или отклоняет сообщение
                    except Exception as e:
                        logger.error(f"Error in callback: {e}")
                        # Отклоняем и отправляем в DLQ
                        await message.reject(requeue=False)

        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")


rabbitmq_client = RabbitMQClient()
