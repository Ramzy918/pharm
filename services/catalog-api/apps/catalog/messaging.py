import json
import logging

import pika
from django.conf import settings

logger = logging.getLogger(__name__)


def publish_order_created(*, order_id: int, user_id: int, email: str, total) -> None:
    try:
        params = pika.URLParameters(settings.AMQP_URL)
        conn = pika.BlockingConnection(params)
        ch = conn.channel()
        ch.exchange_declare(exchange="marketpharm", exchange_type="topic", durable=True)
        body = json.dumps({"order_id": order_id, "user_id": user_id, "email": email, "total": str(total)})
        ch.basic_publish(
            exchange="marketpharm",
            routing_key="order.created",
            body=body.encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
        conn.close()
    except Exception:
        logger.exception("rabbitmq publish order.created failed")
def publish_stock_empty(*, product_id: int, product_name: str) -> None:
    try:
        params = pika.URLParameters(settings.AMQP_URL)
        conn = pika.BlockingConnection(params)
        ch = conn.channel()
        ch.exchange_declare(exchange="marketpharm", exchange_type="topic", durable=True)
        body = json.dumps({"product_id": product_id, "product_name": product_name, "status": "out_of_stock"})
        ch.basic_publish(
            exchange="marketpharm",
            routing_key="stock.empty",
            body=body.encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
        conn.close()
    except Exception:
        logger.exception("rabbitmq publish stock.empty failed")
