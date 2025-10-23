import pika
import json
import os



queue_name = 'tasks'

def send_to_queue(data: dict):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin_user")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin_pass")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    params = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    connection = pika.BlockingConnection(params)

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    message = json.dumps(data)
    channel.basic_publish(
        exchange='',
        routing_key='tasks',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print(f"[x] Sent message: {message}")
    connection.close()