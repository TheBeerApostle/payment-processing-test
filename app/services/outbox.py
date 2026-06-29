
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.payments import PaymentRepository
from app.models import OutboxStatus
from app.rabbitmq import rabbitmq_client
import json

logger = logging.getLogger(__name__)


class OutboxProcessor:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.running = True
        self.max_retries = 3
        self.retry_delay = 5

    async def process_event(self, event, repository):
        try:
            logger.info(f"Processing outbox event {event.id} for payment {event.aggregate_id}")

            payload = event.payload
            payment_id = payload.get("payment_id")

            if not payment_id:
                raise ValueError(f"Missing payment_id in payload: {payload}")

            success = await rabbitmq_client.publish_payment_created(
                payment_id=payment_id,
                payload=payload
            )

            if success:
                await repository.mark_outbox_processed(event.id)
                logger.info(f"Outbox event {event.id} processed successfully")
            else:
                raise Exception("Failed to publish to RabbitMQ")

        except Exception as e:
            logger.error(f"Failed to process outbox event {event.id}: {e}")
            await self.handle_failure(event, repository, str(e))

    async def handle_failure(self, event, repository, error_message):
        event.retry_count += 1

        if event.retry_count >= self.max_retries:
            try:
                await repository.mark_outbox_failed(event.id, error_message)
                logger.error(f"Outbox event {event.id} moved to DLQ after {self.max_retries} retries")
            except Exception as e:
                logger.error(f"Failed to move event to DLQ: {e}")
        else:
            await repository.db.commit()
            logger.warning(f"Outbox event {event.id} will be retried (attempt {event.retry_count})")

    async def process_pending_events(self):
        async with self.db_session_factory() as session:
            repository = PaymentRepository(session)
            events = await repository.get_pending_outbox_events(limit=10)

            for event in events:
                await self.process_event(event, repository)

    async def run(self):
        logger.info("Outbox processor started")
        await rabbitmq_client.connect()

        while self.running:
            try:
                await self.process_pending_events()
                await asyncio.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Outbox processor error: {e}")
                await asyncio.sleep(5)
