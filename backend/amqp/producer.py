import pika

def send_message(message):
    # Establish a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Declare a queue (it will create if it doesn't exist)
    channel.queue_declare(queue='hello')

    # Send a message to the queue
    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body=message)
    print(f" [x] Sent '{message}'")

    # Close the connection
    connection.close()

if __name__ == "__main__":
    message = "Hello, RabbitMQ!"
    send_message(message)
