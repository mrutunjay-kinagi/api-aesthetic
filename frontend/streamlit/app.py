import streamlit as st
import pika
import paho.mqtt.client as mqtt
import requests
import json
import time
import asyncio
import websockets
import xml.etree.ElementTree as ET


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
            response = requests.get(f"http://localhost:5000/events/{symbol}", stream=True)
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

# WebSocket
# WebSocket server URI
uri = "ws://websocket-server:5002"  # Use the service name defined in docker-compose

# Streamlit app
st.title("WebSocket Chat")

async def connect_websocket():
    """Connect to the WebSocket server."""
    try:
        websocket = await websockets.connect(uri)
        return websocket
    except Exception as e:
        st.error(f"Error connecting to WebSocket: {e}")
        return None  # Return None if the connection fails

async def send_message(websocket, message):
    """Send a message through the WebSocket."""
    if websocket is not None:  # Check if websocket is not None
        await websocket.send(message)

async def receive_messages(websocket):
    """Receive messages from the WebSocket and display them."""
    try:
        while True:
            message = await websocket.recv()
            st.write(f"Received: {message}")
    except Exception as e:
        st.error(f"Error receiving messages: {e}")

# Start chat button
if st.button("Start Chat"):
    websocket = asyncio.run(connect_websocket())  # Get the websocket object

    if websocket:  # Check if the connection was successful
        # Start receiving messages
        asyncio.create_task(receive_messages(websocket))  # Create task in the background

        # Input for sending messages
        message = st.text_input("Enter your message:")
        if st.button("Send"):
            asyncio.run(send_message(websocket, message))  # Send the message

        # Optionally, stop the task when you finish
        if st.button("Stop Chat"):
            async def stop_chat():
                await websocket.close()  # Close the connection
                st.write("Chat stopped.")
            asyncio.run(stop_chat())

# Display any errors or notifications
if 'error' in st.session_state:
    st.error(st.session_state['error'])


# SOAP
# Function to send SOAP request to the backend SOAP service
def get_stock_price_soap(symbol):
    soap_url = "http://soap-server:5004/soap"
    headers = {"Content-Type": "text/xml; charset=utf-8"}

    # The SOAP request XML template
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:stock="stock.soap.api">
    <soapenv:Header/>
        <soapenv:Body>
            <stock:getStockPrice>
                <stock:symbol>{symbol}</stock:symbol>
            </stock:getStockPrice>
        </soapenv:Body>
    </soapenv:Envelope>
    """

    # Sending the SOAP request to the API
    response = requests.post(soap_url, data=soap_body, headers=headers)

    # Checking if the response is successful
    if response.status_code == 200:
        # Extracting the response content
        root = ET.fromstring(response.content)
        # Extracting the stock price from the response
        stock_price = root.find('.//{stock.soap.api}getStockPriceResult').text
        return stock_price
    else:
        return None

# Streamlit UI layout
st.title("SOAP API Stock Price Viewer")

# Input field for the stock symbol
stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA)", "AAPL")

# Button to trigger the SOAP request
if st.button("Get Stock Price"):
    stock_price = get_stock_price_soap(stock_symbol)
    if stock_price:
        st.write(f"The stock price of {stock_symbol} is {stock_price}")
    else:
        st.write("Failed to retrieve stock price.")
