import pika

def callback(ch, method, properties, body):
    print(f" [x] Received {body}")

def receive_message():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Declare the same queue
    channel.queue_declare(queue='hello')

    # Subscribe to the queue and specify the callback function
    channel.basic_consume(queue='hello',
                          on_message_callback=callback,
                          auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    receive_message()
