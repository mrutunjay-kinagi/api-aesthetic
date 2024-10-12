import streamlit as st
import pika

def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=message)
    connection.close()

def display_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')

    method_frame, header_frame, body = channel.basic_get(queue='hello', auto_ack=True)
    if method_frame:
        return body.decode()
    else:
        return None

# Streamlit UI
st.title("RabbitMQ - AMQP Protocol Demo")

# Send Message Section
message = st.text_input("Enter message to send:")
if st.button("Send Message"):
    send_message(message)
    st.success(f"Message sent: {message}")

# Receive Message Section
if st.button("Receive Message"):
    received_message = display_message()
    if received_message:
        st.info(f"Received: {received_message}")
    else:
        st.warning("No messages in the queue.")
