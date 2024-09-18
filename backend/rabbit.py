# rabbitmq_consumer.py
import time
import pika
import json
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection setup
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["chat_db"]
messages_collection = db["messages"]

def connect_to_rabbitmq(retries=5, delay=5):
    for attempt in range(retries):
        try:
            connection = pika.BlockingConnection(parameters)
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < retries - 1:
                print(f"RabbitMQ connection failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e

credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
connection = connect_to_rabbitmq()
send_channel = connection.channel()

recv_channel = connection.channel()



# Queue and exchange details
exchange_name = 'my_ex'
queue_name = 'post_queue'
routing_key = 'post_queue'

forward_exchange_name = 'my_ex'
forward_queue_name = 'get_queue'
forward_routing_key = 'get_queue'

# Declare and bind queues for both incoming and forwarding
send_channel.exchange_declare(exchange=exchange_name)
send_channel.queue_declare(queue=queue_name, durable=True)
send_channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

send_channel.queue_declare(queue=forward_queue_name, durable=True)
send_channel.queue_bind(exchange=forward_exchange_name, queue=forward_queue_name, routing_key=forward_routing_key)

# Callback function to process messages
def callback(ch, method, properties, body):
    print("callback")
    try:
        message = json.loads(body)
        # Insert message into MongoDB
        messages_collection.insert_one({
            "content": message["content"],
            "timestamp": datetime.fromisoformat(message["timestamp"])
        })
        print(f"Received and stored message: {message}")

        # Forward message to another queue
        send_channel.basic_publish(
            exchange=forward_exchange_name,
            routing_key=forward_routing_key,
            body=json.dumps(message)
        )
        print(f"Forwarded message: {message}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Start consuming messages
def consume_messages():
    recv_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print('Starting to consume messages...')
    recv_channel.start_consuming()

if __name__ == "__main__":
    consume_messages()