from typing import TYPE_CHECKING
import logging

import pika
from pika.exchange_type import ExchangeType

from app.manager import send_notification
from app.schemas import Notification, NotificationResult
from app.monitoring import send_data_to_zabbix, ZabbixItem
from config import settings


if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


log = logging.getLogger(__name__)


def send_result(
    channel: "BlockingChannel",
    result: NotificationResult,
    incoming_properties: "BasicProperties"
):
    channel.basic_publish(
        exchange="",
        routing_key=incoming_properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=incoming_properties.correlation_id,
            delivery_mode=2,
            content_type="application/json"
        ),
        body=result.model_dump_json().encode()
    )
    log.warning(f"Result sent to {incoming_properties.reply_to}")


def process_new_message(
    ch: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    log.warning("[ ] Start processing message")
    try:
        notification = Notification.model_validate_json(body)
        send_notification(notification)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        log.error(f"Failed to send notification, error: {e}")
        send_data_to_zabbix(
            items=[
                ZabbixItem(key="notify.error", value=str(e)),
            ]
        )
    log.warning("[X] Finished processing message")


def consume_messages(channel: "BlockingChannel") -> None:
    channel.basic_qos(prefetch_count=1)
    channel.exchange_declare(
        exchange=settings.RMQ_EXCHANGE,
        exchange_type=ExchangeType.direct,
        durable=True,
    )
    channel.queue_declare(
        queue=settings.RMQ_QUEUE,
        durable=True
    )
    channel.queue_bind(
        queue=settings.RMQ_QUEUE,
        exchange=settings.RMQ_EXCHANGE,
        routing_key=settings.RMQ_ROUTING_KEY,
    )
    channel.basic_consume(
        queue=settings.RMQ_QUEUE,
        on_message_callback=process_new_message,
    )
    log.warning("Waiting for messages...")
    channel.start_consuming()