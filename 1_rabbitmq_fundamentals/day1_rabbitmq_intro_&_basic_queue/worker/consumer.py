import sys

import pika, json, os, time



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
            print('Connecting to RabbitMQ...')
            connection = pika.BlockingConnection(params)
            print('Connected to RabbitMQ successfully.')
        except pika.exceptions.AMQPConnectionError:
            print('Failed to connect to RabbitMQ. Retrying in 5 seconds...')
            time.sleep(5)

    channel = connection.channel()

    queue_name = 'tasks'
    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f'Worker received: {data}')
        time.sleep(2)
        print(f'Worker task completed')
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)


    print('waiting for message...')
    channel.start_consuming()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)