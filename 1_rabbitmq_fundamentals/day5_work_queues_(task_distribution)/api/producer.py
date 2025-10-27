import pika, json, os

def publish_task(task: dict):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin_user")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin_pass")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    params = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    connection = pika.BlockingConnection(params)

    channel = connection.channel()

    # Declare durable queue
    channel.queue_declare(queue='work_queue', durable=True)

    # Publish persistent message
    body = json.dumps(task)
    channel.basic_publish(
        exchange='',
        routing_key='work_queue',
        body=body,
        # Make message persistent
        properties=pika.BasicProperties(delivery_mode=2,)
    )

    print(f"[x] Sent task: {task}")
    connection.close()