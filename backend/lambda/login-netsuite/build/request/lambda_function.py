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

# NetSuite credentials 
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
