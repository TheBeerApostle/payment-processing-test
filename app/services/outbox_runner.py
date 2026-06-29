#!/usr/bin/env python
import asyncio
import logging
from app.services.outbox import OutboxProcessor
from app.database import AsyncSessionLocal
from app.rabbitmq import rabbitmq_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting outbox processor...")

    try:
        processor = OutboxProcessor(AsyncSessionLocal)
        await processor.run()
    except KeyboardInterrupt:
        logger.info("Outbox processor stopped by user")
    except Exception as e:
        logger.error(f"Outbox processor error: {e}")
        raise
    finally:
        await rabbitmq_client.close()


if __name__ == "__main__":
    asyncio.run(main())