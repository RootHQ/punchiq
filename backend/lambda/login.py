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

# NetSuite Credentials 
NS_ACCOUNT_ID = '5233917_SB1'
NS_CONSUMER_KEY = 'b64b344026224dafbd8eaee73be74f4a942d3676a93b22fab228e95127c98e38'
NS_CONSUMER_SECRET = 'ead49d01ca5065a2055f39706b87113aa07ab7d344e8120c17a884c685d909e6'
NS_TOKEN_ID = '005fc3abbe8d58045f433e269f66c0cedf00b1e67e5d3a934e110978945bf35f'
NS_TOKEN_SECRET = '156ba543c9d1212b8d28991a645feecce6dd6a595a856ce92d701f02ccd26d25'
NS_BASE_URL = 'https://5233917-sb1.suitetalk.api.netsuite.com/services/rest'

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'employee')
table = dynamodb.Table(TABLE_NAME)


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
            # Get punch status and times
            punch_status, times = check_netsuite_punch(int(employee_id))

            if punch_status == "PUNCHED_OUT":
                return build_response(403, {
                    "message": f"You are currently in state: {punch_status} {user.get('empName', 'Unknown')}. Please contact your manager if needed.",
                    "punch_status": punch_status
                })

            token = generate_jwt(
                employee_id, pin, user.get('empName', 'Unknown'), company_id
            )

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


def check_netsuite_punch(employee_id):
    today = datetime.datetime.now().strftime('%#m/%#d/%Y') if os.name == 'nt' else datetime.datetime.now().strftime('%-m/%-d/%Y')
    #today = '05/14/2025'
    query = (
        f"SELECT * FROM customrecord_employee_time_punch "
        f"WHERE custrecord_employee_punched = '{employee_id}' "
        f"AND custrecord_employee_time_punch_date = '{today}' "
    )

    auth = OAuth1WithRealm(
        NS_CONSUMER_KEY, NS_CONSUMER_SECRET,
        NS_TOKEN_ID, NS_TOKEN_SECRET,
        realm=NS_ACCOUNT_ID
    )

    headers = {
        "Content-Type": "application/json",
        "Prefer": "transient"
    }

    url = f"{NS_BASE_URL}/query/v1/suiteql"
    prepared = requests.Request(
        "POST", url, headers=headers, json={"q": query}, auth=auth
    ).prepare()

    session = requests.Session()
    response = session.send(prepared)

    times = {
        "punch_in_time": None,
        "break_start_time": None,
        "break_end_time": None,
        "punch_out_time": None
    }

    if response.status_code == 200:
        data = response.json()
        if data.get('count', 0) > 0:
            record_id = data['items'][0]['id']

            url_record = f"{NS_BASE_URL}/record/v1/customrecord_employee_time_punch/{record_id}"
            record_response = session.get(url_record, headers=headers, auth=auth)
            print("NetSuite Record Response:", record_response.status_code, record_response.text)

            if record_response.status_code == 200:
                item = record_response.json()
                times["punch_in_time"] = item.get('custrecord_punch_in_time')
                times["break_start_time"] = item.get('custrecord_break_start_time')
                times["break_end_time"] = item.get('custrecord_break_end_time')
                times["punch_out_time"] = item.get('custrecord_punch_out_time')

                # Determine Status
                if not times["punch_in_time"] and not times["break_start_time"] and not times["punch_out_time"]:
                    return "NOT_PUNCHED_IN", times
                elif times["punch_in_time"] and not times["break_start_time"] and not times["break_end_time"]:
                    return "PUNCHED_IN", times
                elif times["break_start_time"] and not times["break_end_time"] and not times["punch_out_time"]:
                    return "ON_BREAK", times
                elif times["break_start_time"] and times["break_end_time"] and not times["punch_out_time"]:
                    return "FINISHED_BREAK", times
                elif not times["break_start_time"] and times["break_end_time"] and not times["punch_out_time"]:
                    return "FINISHED_BREAK", times
                elif times["punch_out_time"]:
                    return "PUNCHED_OUT", times

    return "NOT_PUNCHED_IN", times


def generate_jwt(employee_id, pin, empName, company_id):
    encrypted_pin = encode_pin(pin)
    payload = {
        "sub": employee_id,
        "pin_encrypted": encrypted_pin,
        "empName": empName,
        "company_id": company_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


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
