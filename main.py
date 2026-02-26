import logging

from app.core import configure_logging
from app.db import init_db
from app.rabbit import RabbitBase
from app.consumer import consume_messages


def main():
    configure_logging(level=logging.WARNING)
    init_db()
    with RabbitBase() as rabbit:
        consume_messages(channel=rabbit.channel)


if __name__ == '__main__':
    main()