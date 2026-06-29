import asyncio
import random
import json
from app.models import PaymentStatus
from app.utils.webhook import send_webhook
from app.schemas import WebhookPayload
from app.repository.payments import PaymentRepository
from app.rabbitmq import rabbitmq_client
import logging

logger = logging.getLogger(__name__)


class PaymentConsumer:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.running = True
        self.max_retries = 3

    async def process_payment_message(self, message):
        try:
            data = json.loads(message.body.decode())
            payment_id = data.get("payment_id")

            if not payment_id:
                logger.error("Message missing payment_id")
                await message.ack()
                return

            logger.info(f"Processing payment {payment_id} from RabbitMQ")

            async with self.db_session_factory() as session:
                success = await self.process_payment(payment_id, session)

            if success:
                await message.ack()
                logger.info(f"Payment {payment_id} processed and message acknowledged")
            else:
                await message.reject(requeue=False)
                logger.error(f"Payment {payment_id} processing failed, message sent to DLQ")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {e}")
            await message.reject(requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await message.reject(requeue=False)

    async def process_payment(self, payment_id: str, db) -> bool:
        repository = PaymentRepository(db)
        payment = await repository.get_by_id(payment_id)

        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return False

        try:
            processing_time = random.randint(2, 5)
            logger.info(f"Processing payment {payment_id} for {processing_time} seconds")
            await asyncio.sleep(processing_time)

            if random.random() < 0.9:
                status = PaymentStatus.SUCCEEDED
                logger.info(f"Payment {payment_id} succeeded")
            else:
                status = PaymentStatus.FAILED
                logger.error(f"Payment {payment_id} failed")

            await repository.update_status(payment_id, status)

            webhook_payload = WebhookPayload(
                payment_id=payment_id,
                status=status.value,
                amount=payment.amount,
                currency=payment.currency
            )

            webhook_success = await send_webhook(
                url=payment.webhook_url,
                payload=webhook_payload,
                max_retries=3
            )

            if webhook_success:
                logger.info(f"Webhook sent successfully for payment {payment_id}")
            else:
                logger.warning(f"Webhook failed after 3 retries for payment {payment_id}")

            logger.info(f"Payment {payment_id} processed successfully")
            return True

        except Exception as e:
            logger.error(f"Error processing payment {payment_id}: {e}")
            await repository.update_status(payment_id, PaymentStatus.FAILED)
            return False

    async def run(self):
        logger.info("Payment consumer started")
        await rabbitmq_client.connect()

        try:
            await rabbitmq_client.consume_payments(self.process_payment_message)
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise

