import json
import logging
import os
import sys
import time

import pika

logging.basicConfig(level=logging.INFO, format="%(asctime)s [worker] %(message)s")
logger = logging.getLogger(__name__)

AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE = "marketpharm"
QUEUE = "notifications"
ROUTING_KEY = "order.created"


def main():
    while True:
        try:
            params = pika.URLParameters(AMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
            channel.queue_declare(queue=QUEUE, durable=True)
            channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key="order.created")
            channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key="stock.empty")
            logger.info("En écoute sur %s (order.created & stock.empty)", QUEUE)

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    payload = {"raw": body.decode("utf-8", errors="replace")}
                
                if method.routing_key == "order.created":
                    logger.info("Notification commande — simulation envoi e-mail : %s", payload)
                elif method.routing_key == "stock.empty":
                    logger.warning("ALERTE STOCK — Produit '%s' (ID:%s) est en rupture !", 
                                   payload.get("product_name"), payload.get("product_id"))
                else:
                    logger.info("Notification reçue [%s]: %s", method.routing_key, payload)
                
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_qos(prefetch_count=10)
            channel.basic_consume(queue=QUEUE, on_message_callback=callback)
            channel.start_consuming()
        except (pika.exceptions.AMQPConnectionError, OSError) as e:
            logger.warning("Connexion RabbitMQ indisponible (%s), nouvel essai dans 3s…", e)
            time.sleep(3)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    main()
