import logging

from config import configure_logging, settings
from app.db import init_db
from app.rabbit import RabbitBase, consume_messages


log = logging.getLogger(__name__)


def main():
    configure_logging(level=logging.WARNING)
    init_db()

    if settings.DEBUG:
        log.warning("Running in DEBUG mode — all emails will be redirected to 'admin' group")

    with RabbitBase() as rabbit:
        consume_messages(channel=rabbit.channel)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")