from src.service.event_publisher_service import EventPublisher
from src.setup.api_settings import AppSettings


settings = AppSettings()
def get_event_pub_service()->EventPublisher:
    return EventPublisher(settings.TOPIC_ARN)