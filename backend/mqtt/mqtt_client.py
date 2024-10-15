import paho.mqtt.client as mqtt

# MQTT broker configuration
BROKER = "localhost"
PORT = 1883
TOPIC = "stocks/AAPL"

# Callback when connecting to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)

# Callback when receiving a message
def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()} from topic: {msg.topic}")

# Initialize MQTT client
client = mqtt.Client()

# Assign the callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(BROKER, PORT, 60)

# Blocking call to process network traffic and handle callbacks
client.loop_forever()
