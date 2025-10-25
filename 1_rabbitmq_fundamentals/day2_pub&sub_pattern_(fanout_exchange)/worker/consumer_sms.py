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
            print('[SMS Service] is connecting to RabbitMQ...')
            connection = pika.BlockingConnection(params)
            print('[SMS Service] connected to RabbitMQ successfully.')
        except pika.exceptions.AMQPConnectionError:
            print('[SMS Service] failed to connect to RabbitMQ. Retrying in 5 seconds...')
            time.sleep(5)

    channel = connection.channel()
    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    # Each subscriber gets a unique queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind queue to exchange
    channel.queue_bind(exchange='logs', queue=queue_name)
    print(f"[SMS Service] Waiting for messages on {queue_name}")

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f"[SMS Service] Sending sms for: {data}")
        time.sleep(2)
        print("[SMS Service] Done.")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)