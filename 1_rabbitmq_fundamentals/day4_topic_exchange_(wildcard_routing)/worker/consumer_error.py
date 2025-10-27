import pika, json, os, time, sys


def main():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin_user")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin_pass")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    params = pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)

    connection = None
    while not connection:
        try:
            print('[ERROR Service] is connecting to RabbitMQ...')
            connection = pika.BlockingConnection(params)
            print('[ERROR Service] connected to RabbitMQ successfully.')
        except pika.exceptions.AMQPConnectionError:
            print('[ERROR Service] failed to connect to RabbitMQ. Retrying in 5 seconds...')
            time.sleep(5)

    channel = connection.channel()
    channel.exchange_declare(exchange='topic_events', exchange_type='topic')

    queue_name = 'error_service_queue'
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange='topic_events', queue=queue_name, routing_key='#.error')

    print('[ERROR Worker] Listening for all error events...')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f"[ERROR Worker] Received: {method.routing_key} -> {data}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)

