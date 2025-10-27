import pika, json, os, sys, time


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
            print('[Worker] is connecting to RabbitMQ...')
            connection = pika.BlockingConnection(params)
            print('[Worker] connected to RabbitMQ successfully.')
        except pika.exceptions.AMQPConnectionError:
            print('[Worker] failed to connect to RabbitMQ. Retrying in 5 seconds...')
            time.sleep(5)

    channel = connection.channel()

    channel.queue_declare(queue='work_queue', durable=True)
    channel.basic_qos(prefetch_count=1) # Fair dispatch

    print("[Worker] Waiting for tasks. To exit press CTRL+C")

    def callback(ch, method, properties, body):
        task = json.loads(body)
        print(f'[Worker] received task: {task}')
        time.sleep(5)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f'[Worker] Done processing: {task}]')

    channel.basic_consume(queue='work_queue', on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)

