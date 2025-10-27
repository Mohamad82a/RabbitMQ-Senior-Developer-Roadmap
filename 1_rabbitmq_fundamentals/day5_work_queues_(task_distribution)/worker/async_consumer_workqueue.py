import asyncio
import pika, json, os, sys, time



async def process_task(task):
    task_type = task.get('task_type')
    print(f'[Worker] Processing job: {task_type} | File: {task.get('file')}')
    await asyncio.sleep(3)
    print(f'[Worker] Done: {task}')



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

    async def handle_task(ch, method, properties, body):
        task = json.loads(body)
        print(f'[Worker] received task: {task}')
        try:
            await process_task(task)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f'[Worker] Done processing: {task}]')
        except Exception as e:
            print(f"[Worker] Error processing job: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def callback(ch, method, properties, body):
        asyncio.run(handle_task(ch, method, properties, body))

    channel.basic_consume(queue='work_queue', on_message_callback=callback)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)

