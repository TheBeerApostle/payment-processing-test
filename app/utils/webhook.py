import aiohttp
import asyncio
import logging
from app.schemas import WebhookPayload

logger = logging.getLogger(__name__)


async def send_webhook(url: str, payload: WebhookPayload, retry_count: int = 0, max_retries: int = 3) -> bool:
    """Отправка webhook с ретраями"""
    headers = {
        "Content-Type": "application/json",
        "X-Payment-Signature": "test-signature"
    }

    delay = 2 ** retry_count

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    url,
                    json=payload.model_dump(mode='json'),
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status in [200, 201, 202, 204]:
                    logger.info(f"Webhook sent successfully to {url}")
                    return True
                else:
                    logger.warning(f"Webhook returned status {response.status} for {url}")

                    if retry_count < max_retries:
                        logger.info(f"Retrying webhook in {delay} seconds (attempt {retry_count + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        return await send_webhook(url, payload, retry_count + 1, max_retries)
                    return False

        except Exception as e:
            logger.error(f"Webhook error for {url}: {e}")

            if retry_count < max_retries:
                logger.info(f"Retrying webhook in {delay} seconds (attempt {retry_count + 1}/{max_retries})")
                await asyncio.sleep(delay)
                return await send_webhook(url, payload, retry_count + 1, max_retries)
            return False


