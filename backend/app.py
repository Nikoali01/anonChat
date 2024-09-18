# app.py
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import pika
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import threading

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")

client = MongoClient(MONGODB_URI)
db = client["chat_db"]
messages_collection = db["messages"]

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, int(RABBITMQ_PORT)))

send_channel = connection.channel()

recv_channel = connection.channel()

exchange_name = ''
queue_name = 'post_queue'
routing_key = ''

forward_exchange_name = ''
forward_queue_name = 'get_queue'
forward_routing_key = ''


send_channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
send_channel.queue_declare(queue=queue_name)
send_channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

send_channel.exchange_declare(exchange=forward_exchange_name, exchange_type='topic')
send_channel.queue_declare(queue=forward_queue_name)
send_channel.queue_bind(exchange=forward_exchange_name, queue=forward_queue_name, routing_key=forward_routing_key)

app = FastAPI()


@app.get("/messages_count/")
async def messages_count():
    try:
        count = messages_collection.count_documents({})
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def consume_messages():
    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            messages_collection.insert_one({
                "content": message["content"],
                "timestamp": datetime.fromisoformat(message["timestamp"])
            })
            print(f"Received and stored message: {message}")

            send_channel.basic_publish(
                exchange=forward_exchange_name,
                routing_key=forward_routing_key,
                body=json.dumps(message)
            )
            print(f"Forwarded message: {message}")
        except Exception as e:
            print(f"Error processing message: {e}")

    recv_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print('Starting to consume messages...')
    recv_channel.start_consuming()


threading.Thread(target=consume_messages, daemon=True).start()
