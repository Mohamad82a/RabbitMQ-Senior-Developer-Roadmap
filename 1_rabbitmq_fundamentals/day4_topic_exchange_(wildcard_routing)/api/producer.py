import pika, os, json

def publish_event(routing_key: str, message: dict):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin_user")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin_pass")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    params = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    connection = pika.BlockingConnection(params)

    channel = connection.channel()

    # Declare a direct exchange
    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

    body = json.dumps(message)
    channel.basic_publish(exchange='topic_events', routing_key=routing_key, body=body)
    print(f"[x] Sent {routing_key}: {message}")
    connection.close()
