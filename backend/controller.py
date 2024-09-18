# api_service.py

from fastapi import FastAPI, HTTPException
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

app = FastAPI()

# API endpoint to get message count from MongoDB
@app.get("/messages/count")
async def messages_count():
    try:
        count = messages_collection.count_documents({})
        return {"count": count}
    except Exception as e:
        return {"code": 500, "message": str(e)}