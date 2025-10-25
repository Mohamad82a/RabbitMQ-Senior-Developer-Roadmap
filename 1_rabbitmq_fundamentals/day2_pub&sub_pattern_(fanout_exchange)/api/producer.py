import pika
import json
import os


def publish_event(data: dict):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin_user")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin_pass")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    params = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    connection = pika.BlockingConnection(params)

    channel = connection.channel()

    # Declare a fanout exchange
    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    message = json.dumps(data)
    channel.basic_publish(exchange='logs', routing_key='', body=message)
    print(f"[x] Sent event: {message}")
    connection.close()
