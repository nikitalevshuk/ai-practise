from amplitude import Amplitude, BaseEvent

from task1.config import settings
from task1.logger import logger

amplitude_client = Amplitude(settings.AMPLITUDE_API_KEY)

def send_event_to_amplitude(user_id: str, event_name: str, event_properties: dict | None = None):
    logger.info("Началось выполнение функции send_event_to_amplitude")

    event = BaseEvent(user_id=user_id, event_type=event_name, event_properties=event_properties)
    amplitude_client.track(event)

    logger.info(f"Отправлен event: {event_name} для user`a {user_id}")