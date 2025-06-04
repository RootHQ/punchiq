# app/main.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import boto3
import os
import uuid
from datetime import datetime
from typing import List

app = FastAPI()

# AWS configuration
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "https://sqs.us-east-2.amazonaws.com/123456789012/time-off-queue")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "TimeOffRequests")
sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)

class TimeOffRequest(BaseModel):
    date: str
    payCode: str
    length: str
    notes: str

@app.post("/time-off")
async def handle_time_off(request: TimeOffRequest):
    try:
        message = request.dict()

        # Generate unique ID
        record_id = str(uuid.uuid4())
        message["id"] = record_id
        message["timestamp"] = datetime.now().isoformat()

        # Send to SQS
        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=str(message)
        )

        # Save to DynamoDB
        table.put_item(Item=message)

        return {"message": "Request processed successfully", "id": record_id}
    except Exception as e:
        return {"error": str(e)}

@app.get("/time-off-all")
def get_all_requests():
    try:
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"message": "Time Off API is up"}
