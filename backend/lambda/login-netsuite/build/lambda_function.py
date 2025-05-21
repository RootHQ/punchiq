import json
import jwt
import datetime
import os
import boto3
import requests
from boto3.dynamodb.conditions import Key
from requests_oauthlib import OAuth1

# Secret key for JWT
JWT_SECRET = os.environ.get('JWT_SECRET', 'your_secret_key')
JWT_ALGORITHM = 'HS256'

# NetSuite credentials (¡en producción usa Secrets Manager!)
NS_ACCOUNT_ID = '5233917_SB1'
NS_CONSUMER_KEY = 'b1e0dfa51d6d245a8e1d9e70cb1180e4a354b59e6387428bf0a897410a28ab75'
NS_CONSUMER_SECRET = '3586a0932b6a060467a62ca2f51c5b723af697033b57e1fb86711450775b6463'
NS_TOKEN_ID = 'bba3fcb972114cf0a157521792bfe73423e40bf6dfa631969465caedf2495671'
NS_TOKEN_SECRET = 'db8e84de263f7f8f23a322086e044b3ca8aeab3c3b1890f5564d7022c60cc9ff'
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
            # Verifica en NetSuite si ya trabajó hoy
            already_worked = check_netsuite_punch(int(employee_id))
            if already_worked:
                return build_response(403, {"message": "You have already worked today. Please contact your manager."})

            token = generate_jwt(employee_id)
            return build_response(200, {
                "message": "Login successful",
                "employee_name": user.get('empName', 'Unknown'),
                "token": token
            })
        else:
            return build_response(401, {"message": "Invalid credentials"})

    except Exception as e:
        print("Error:", str(e))
        return build_response(500, {"message": "Internal server error"})


def check_netsuite_punch(employee_id):
    today = datetime.datetime.now().strftime('%-m/%-d/%Y')

    query = f"""
    SELECT * FROM customrecord_employee_time_punch 
    WHERE custrecord_employee_punched = '{employee_id}'
    AND custrecord_employee_time_punch_date = '{today}'
    AND custrecord_corresponding_time_record IS NULL
    AND custrecord_corresponding_overtime_record IS NULL
    """

    auth = OAuth1(NS_CONSUMER_KEY, NS_CONSUMER_SECRET, NS_TOKEN_ID, NS_TOKEN_SECRET, signature_method='HMAC-SHA256')
    headers = {'Content-Type': 'application/json'}
    url = f"{NS_BASE_URL}/query/v1/suiteql"

    response = requests.post(url, headers=headers, auth=auth, json={"q": query})
    print("NetSuite SuiteQL Response:", response.status_code, response.text)

    if response.status_code == 200:
        data = response.json()
        if data.get('count', 0) > 0:
            return True
    return False

def generate_jwt(employee_id):
    payload = {
        "sub": employee_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

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
