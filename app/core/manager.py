from schemas import Notification
from services import send_email
import logging


log = logging.getLogger(__name__)


def send_notification(notification: Notification):
    strategies = {
        "email": send_email
        # "telegram": send_telegram,
    }
    for strategy in set(notification.methods):
        if not strategies.get(strategy):
            log.warning(f"The strategy {strategy} is not currently supported.")
            continue
        strategies[strategy](notification)
    return True