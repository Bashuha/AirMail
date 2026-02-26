from typing import TYPE_CHECKING
import logging

import pika
from pika.exchange_type import ExchangeType

from app.core import settings, send_notification
from app.schemas import Notification, NotificationResult


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
    error_msg = None
    status: str = "success"
    try:
        notification = Notification.model_validate_json(body)
        send_notification(notification)
    except Exception as e:
        log.error(f"Failed to send notification, error: {e}")
        error_msg = str(e)
        status = "error"

    result = NotificationResult(
        status=status,
        error_message=error_msg
    )
    try:
        send_result(
            channel=ch,
            result=result,
            incoming_properties=properties,
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        log.warning("[X] Finished processing message")
    except Exception as e:
        log.error("Error processing message: %s", e, exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def consume_messages(channel: "BlockingChannel") -> None:
    channel.basic_qos(prefetch_count=1)
    channel.exchange_declare(
        exchange=settings.RMQ_EXCHANGE,
        exchange_type=ExchangeType.topic,
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