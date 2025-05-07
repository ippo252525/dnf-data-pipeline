import asyncio

from pyneople.config.config import Settings
import logging

logger = logging.getLogger(__name__)

async def count_requests_per_second(shutdown_event : asyncio.Event):
    """
    1초에 얼마나 많은 요청을 하는지 확인하는 함수
    """
    while not shutdown_event.is_set():
        await asyncio.sleep(1)
        logger.info(f"초당 요청 수: {Settings.request_count}")
        Settings.request_count = 0