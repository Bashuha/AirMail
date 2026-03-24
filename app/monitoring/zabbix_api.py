from collections import namedtuple
from typing import List

from zabbix_utils import Sender
from zabbix_utils.types import ItemValue

from config import settings


ZabbixItem = namedtuple("ZabbixItem", ["key", "value"])


class ZabbixKey:
    SEND_ERROR = "notify.send.error"


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