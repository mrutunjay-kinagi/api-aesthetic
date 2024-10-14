import streamlit as st
import pika
import paho.mqtt.client as mqtt
import requests
import json
import time

# AMQP
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

# # MQTT
MQTT_BROKER = "mosquitto"  # This should match the service name in docker-compose
MQTT_PORT = 1883
TOPIC = "test/topic"

# MQTT Callback when a message is received
def on_message(client, userdata, message):
    print("Message received")  # Debugging
    st.session_state["mqtt_message"] = message.payload.decode("utf-8")
    print(f"Received message: {st.session_state['mqtt_message']}")  # Debugging

# Initialize MQTT client
def init_mqtt_client():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    print("Connected to MQTT broker")  # Debugging
    client.subscribe(TOPIC)  # Subscribe to the topic
    client.loop_start()  # Start the loop in a separate thread
    return client

# Initialize MQTT client if not already done
if "mqtt_client" not in st.session_state:
    st.session_state["mqtt_client"] = init_mqtt_client()

# MQTT Publisher (to send messages)
def publish_message(message):
    st.session_state["mqtt_client"].publish(TOPIC, message)
    st.success(f"Message '{message}' published to topic '{TOPIC}'")

# Streamlit UI
st.title("MQTT Demo")

# Message Input for publishing
message = st.text_input("Enter message to publish:", "")
if st.button("Send Message"):
    publish_message(message)

# Display received messages
if "mqtt_message" in st.session_state:
    st.write(f"Received Message: {st.session_state['mqtt_message']}")
else:
    st.write("No messages received yet.")

#SSE
st.title("SSE DEMO - Live Stock Price Tracker")

# Input for stock symbol
stock_symbol = st.text_input("Enter Stock Symbol", "AAPL")

# Create a placeholder for the data
data_placeholder = st.empty()

# Function to fetch SSE data with retry
def fetch_sse_data_with_retry(symbol, retries=5, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(f"http://localhost:5001/events/{symbol}", stream=True)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.iter_lines()
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            else:
                raise e

# Listening to the SSE stream
if stock_symbol:
    try:
        sse_data = fetch_sse_data_with_retry(stock_symbol)
        for line in sse_data:
            if line:
                data = json.loads(line.decode('utf-8')[5:])  # Skip "data: " prefix
                stock = data['stock']
                price = data['price']
                data_placeholder.write(f"Stock: {stock}, Price: {price}")
    except Exception as e:
        data_placeholder.write(f"Error: {e}")