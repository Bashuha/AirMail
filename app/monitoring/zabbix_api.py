import logging
import threading
import time
from collections import namedtuple
from typing import List

from zabbix_utils import Sender
from zabbix_utils.types import ItemValue

from config import settings


log = logging.getLogger(__name__)

HEARTBEAT_INTERVAL_SECONDS = 5 * 60

ZabbixItem = namedtuple("ZabbixItem", ["key", "value"])


class ZabbixKey:
    SEND_ERROR = "notify.send.error"
    HEARTBEAT = "notify.heartbeat"


def send_data_to_zabbix(items: List[ZabbixItem]) -> None:
    data = [
        ItemValue(
            host=settings.ZABBIX_HOSTNAME,
            key=item.key,
            value=item.value,
        ) for item in items
    ]

    zab_sender = Sender(
        server=settings.ZABBIX_URL,
        port=settings.ZABBIX_PORT,
    )

    zab_sender.send(data)


def _heartbeat_loop() -> None:
    while True:
        try:
            send_data_to_zabbix([ZabbixItem(key=ZabbixKey.HEARTBEAT, value=1)])
        except Exception:
            log.exception("Zabbix heartbeat failed")
        time.sleep(HEARTBEAT_INTERVAL_SECONDS)


def start_heartbeat() -> None:
    thread = threading.Thread(
        target=_heartbeat_loop,
        name="zabbix-heartbeat",
        daemon=True,
    )
    thread.start()