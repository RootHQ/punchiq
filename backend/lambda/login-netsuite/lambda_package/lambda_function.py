import json
import jwt
import datetime
import os

# Secret key to sign JWTs (keep this secret!)
JWT_SECRET = os.environ.get('JWT_SECRET', 'your_secret_key_here')
JWT_ALGORITHM = 'HS256'

def lambda_handler(event, context):
    if event['httpMethod'] == 'OPTIONS':
        return build_response(200, 'OK')

    try:
        body = json.loads(event.get('body', '{}'))
        pin = body.get('pin')
        employee_id = body.get('employee_id')

        if employee_id == '233' and pin == '2618':
            token = generate_jwt(employee_id)
            response = {
                "message": "Login successful",
                "token": token
            }
            return build_response(200, response)
        else:
            return build_response(401, {"message": "Invalid credentials"})

    except Exception as e:
        print("Error:", e)
        return build_response(500, {"message": "Internal server error"})

def generate_jwt(employee_id):
    payload = {
        'employee_id': employee_id,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def build_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }
