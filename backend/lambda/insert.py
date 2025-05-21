import json
import jwt
import datetime
import os
import boto3
from boto3.dynamodb.conditions import Key

# Secret key for JWT 
JWT_SECRET = os.environ.get('JWT_SECRET', 'your_secret_key')
JWT_ALGORITHM = 'HS256'

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'employee') 
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    print("===== EVENTO RECIBIDO =====")
    print(json.dumps(event))  # can see in CloudWatch

    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return build_response(200, {"message": "CORS preflight passed"})

    try:
        body = json.loads(event.get('body', '{}'))
        employee_id = body.get('employee_id')
        pin = body.get('pin')
        company_id = body.get('company_id')


        response = table.get_item(
            Key={
                'employee_id': int(employee_id),
            }
        )
        print("===== RESPONSE =====")
        user = response.get('Item')
        print(user)

        user = response.get('Item')
                # Validación de campos
        if user and user.get('pin') == pin and user.get('company_id') == company_id:
            token = generate_jwt(employee_id)
            return build_response(200, {
                "message": "Login successful",
                "employee_name": user.get('empName', 'Unknown'),
                "token": token
            })
        else:
            return build_response(401, {"message": "Invalid credentials"})

    except Exception as e:
        print("Error:", e)
        return build_response(500, {"message": "Internal server error"})

# JWT helper
def generate_jwt(employee_id):
    payload = {
        "sub": employee_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# Generic response builder with CORS headers
def build_response(status_code, body):
    return {
        "statusCode": status_code,
        
        "body": json.dumps(body)
    }
