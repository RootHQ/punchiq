import json
import jwt
import datetime
import os
import boto3
import requests
from boto3.dynamodb.conditions import Key
from requests_oauthlib import OAuth1
from requests.auth import AuthBase
import base64

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your_secret_key')
JWT_ALGORITHM = 'HS256'

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'employee')
table = dynamodb.Table(TABLE_NAME)

TABLE_settings = os.environ.get('DYNAMODB_TABLE', 'setting')
tableSettings = dynamodb.Table(TABLE_settings)

punch_table = dynamodb.Table(os.environ.get('PUNCH_TABLE', 'Punch')) 

def lambda_handler(event, context):
    print("===== EVENT RECEIVED =====")
    print(json.dumps(event))

    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return build_response(200, {"message": "CORS preflight passed"})

    try:
        body = json.loads(event.get('body', '{}'))
        employee_id = body.get('employee_id')
        pin = body.get('pin')
        company_id = body.get('company_id')

        response = table.get_item(Key={'employee_id': int(employee_id)})
        user = response.get('Item')

        if user and user.get('pin') == pin and user.get('company_id') == company_id and user.get('active') == True:
            # Consulta primero en DynamoDB (Punch Table)
            today_punch = get_today_punch_record(employee_id, company_id)

            if today_punch:
                times = {
                    "punch_in_time": today_punch.get('punch_in_time'),
                    "break_start_time": today_punch.get('break_start_time'),
                    "break_end_time": today_punch.get('break_end_time'),
                    "punch_out_time": today_punch.get('punch_out_time')
                }
                punch_status = determine_punch_status(times)
            else:
                # Si no hay en DynamoDB, consulta en NetSuite
                punch_status = "NOT_PUNCHED_IN"
                times = {
                    "punch_in_time": "",
                    "break_start_time":"",
                    "break_end_time": "",
                    "punch_out_time": ""
                }

            if punch_status == "PUNCHED_OUT":
                return build_response(403, {
                    "message": f"You are currently in state: {punch_status} {user.get('empName', 'Unknown')}. Please contact your manager if needed.",
                    "punch_status": punch_status
                })

            token = generate_jwt(employee_id, pin, user.get('empName', 'Unknown'), company_id)

            return build_response(200, {
                "message": "Login successful, " + str(punch_status),
                "employee_name": user.get('empName', 'Unknown'),
                "punch_status": punch_status,
                "punch_in_time": times.get('punch_in_time'),
                "break_start_time": times.get('break_start_time'),
                "break_end_time": times.get('break_end_time'),
                "punch_out_time": times.get('punch_out_time'),
                "token": token
            })
        else:
            return build_response(401, {"message": "Invalid credentials"})

    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
        return build_response(500, {"message": f"Internal server error: {str(e)}"})


def get_today_punch_record(employee_id, company_id):
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    response = punch_table.query(
        KeyConditionExpression=Key('employeeId').eq(int(employee_id)) & Key('Date').eq(today),
        FilterExpression="companyId = :company_id",
        ExpressionAttributeValues={
            ":company_id": company_id
        }
    )

    items = response.get('Items', [])
    if items:
        return items[0]
    return None


def determine_punch_status(times):
    if not times["punch_in_time"] and not times["punch_in_time"] and not times["break_start_time"] and not times["punch_out_time"]:
        return "NOT_PUNCHED_IN"
    elif times["punch_in_time"] and not times["break_start_time"] and not times["punch_out_time"]:
        return "PUNCHED_IN"
    elif times["break_start_time"] and not times["break_end_time"] and not times["punch_out_time"]:
        return "ON_BREAK"
    elif times["punch_out_time"]:
        return "PUNCHED_OUT"
    else:
        return "UNKNOWN"


def generate_jwt(employee_id, pin, empName, company_id):
    encrypted_pin = encode_pin(pin)
    payload = {
        "sub": employee_id,
        "pin_encrypted": encrypted_pin,
        "empName": empName,
        "company_id": company_id,
        "exp":  datetime.datetime.now() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def encode_pin(pin):
    return base64.b64encode(pin.encode()).decode()


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    }


class OAuth1WithRealm(AuthBase):
    def __init__(self, client_key, client_secret, resource_owner_key, resource_owner_secret, realm, **kwargs):
        self.realm = realm
        self.auth = OAuth1(
            client_key, client_secret,
            resource_owner_key, resource_owner_secret,
            realm=realm,
            signature_method='HMAC-SHA256',
            signature_type='AUTH_HEADER',
            **kwargs
        )

    def __call__(self, r):
        r = self.auth(r)
        auth_header = r.headers.get('Authorization')
        if isinstance(auth_header, bytes):
            auth_header = auth_header.decode('utf-8')
        r.headers['Authorization'] = auth_header.replace('OAuth ', f'OAuth realm="{self.realm}",', 1)
        return r
