import asyncio

from concurrent.futures import ThreadPoolExecutor

from services.amplitude_api import send_event_to_amplitude

executor = ThreadPoolExecutor(max_workers=5)

async def executor_send_event(user_id: str, event_name: str, event_properties: dict = None):
    logger.info("Попали в executor_send_event")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor, send_event_to_amplitude, user_id, event_name, event_properties)

