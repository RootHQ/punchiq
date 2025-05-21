# backend/lambda/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import boto3
import os
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# ✅ CORS Middleware (IMPORTANT for Angular frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Use specific domains in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "punchiq-logs"))

# Mock login data
data = {
    "1001": {"pin": "1234", "employee_id": "Alice"},
    "1002": {"pin": "4321", "employee_id": "Bob"}
}

# Schemas
class LoginRequest(BaseModel):
    employee_id: str
    pin: str

class PunchRequest(BaseModel):
    employee_id: str
    pin: str
    action: str
    timestamp: str = datetime.utcnow().isoformat()

# Routes
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/login")
def login(req: LoginRequest):
    user = data.get(req.employee_id)
    if not user or user["pin"] != req.pin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "employee_name": user["name"]}

@app.post("/punch")
def punch(req: PunchRequest):
    try:
        user = data.get(req.employee_id)
        if not user or user["pin"] != req.pin:
            raise HTTPException(status_code=401, detail="Unauthorized punch")

        item = {
            "employee_id": req.employee_id,
            "timestamp": req.timestamp,
            "action": req.action,
            "employee_name": user["name"]
        }
        table.put_item(Item=item)
        return {"message": "Punch recorded", "data": item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lambda handler
handler = Mangum(app)
