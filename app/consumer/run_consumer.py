#!/usr/bin/env python
import asyncio
import logging
from app.consumer.payment_consumer import PaymentConsumer
from app.database import AsyncSessionLocal
from app.rabbitmq import rabbitmq_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting payment consumer...")

    try:
        consumer = PaymentConsumer(AsyncSessionLocal)
        await consumer.run()
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception as e:
        logger.error(f"Consumer error: {e}")
        raise
    finally:
        await rabbitmq_client.close()


if __name__ == "__main__":
    asyncio.run(main())