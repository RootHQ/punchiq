import json
import boto3
import os
import requests
from datetime import datetime
from requests_oauthlib import OAuth1
from requests.auth import AuthBase

# AWS Resources
sqs = boto3.client('sqs')
QUEUE_URL = ''


# NetSuite Credentials 
NS_ACCOUNT_ID = ''
NS_CONSUMER_KEY = ''
NS_CONSUMER_SECRET = ''
NS_TOKEN_ID = ''
NS_TOKEN_SECRET = ''
NS_BASE_URL = ''
def lambda_handler(event, context):
    if 'Records' not in event:
        print("No 'Records' found. Are you testing manually?")
        return

    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            print(f"📨 Processing message: {message}")

            response_status = process_punch(message)

            receipt_handle = record.get('receiptHandle', '')
            if response_status and receipt_handle.startswith('AQEB'):
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                print("✅ Message deleted from SQS.")
            else:
                print("⚠️ Skipping delete_message due to invalid or missing receiptHandle.")

        except Exception as e:
            print(f"❌ Error processing message: {e}")

def process_punch(data):
    auth = OAuth1WithRealm(
        NS_CONSUMER_KEY, NS_CONSUMER_SECRET,
        NS_TOKEN_ID, NS_TOKEN_SECRET,
        realm=NS_ACCOUNT_ID
    )

    today = datetime.now().strftime('%m/%d/%Y')

    employee_id = data.get('employeeId')

    # Step 1: Query for existing Punch Record
    existing_record_id = query_existing_punch(auth, employee_id, today)

    if existing_record_id:
        print(f"Existing Punch Record Found: {existing_record_id}")
        return update_punch_record(auth, existing_record_id, data)
    else:
        print("No existing Punch Record found.")
        #return create_punch_record(auth, data)

def query_existing_punch(auth, employee_id, today):
    url = f"{NS_BASE_URL}/query/v1/suiteql"
    headers = {"Content-Type": "application/json", "Prefer": "transient"}
    query = f"""SELECT * FROM customrecord_employee_time_punch WHERE custrecord_employee_punched = '{employee_id}' AND custrecord_employee_time_punch_date = '{today}'"""
    payload = {"q": query}
    
    print(f"Npayload: {payload}")

    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth)  # ✅ Changed to POST
        if response.status_code == 200:
            results = response.json().get('items', [])
            if results:
                return results[0].get('id')
        else:
            print(f"NetSuite Query Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Exception during NetSuite Query: {e}")
    return None


def create_punch_record(auth, data):
    url = f"{NS_BASE_URL}/record/v1/customrecord_employee_time_punch"
    headers = {"Content-Type": "application/json"}

    payload = {
        "custrecord_employee_punched": data.get('employeeId'),
        "custrecord_employee_time_punch_date": data.get('Date'),
        "custrecord_punch_in_time": data.get('punch_in_time'),
        "custrecord_break_start_time": data.get('break_start_time'),
        "custrecord_break_end_time": data.get('break_end_time'),
        "custrecord_punch_out_time": data.get('punch_out_time')
    }

    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth)
        if response.status_code in [200, 201]:
            print("✅ Punch Record Created in NetSuite.")
            created_id = response.json().get('id')
            if created_id:
                return True
        else:
            print(f"NetSuite Create Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Exception during Punch Create: {e}")
    return False

def update_punch_record(auth, record_id, data):
    url = f"{NS_BASE_URL}/record/v1/customrecord_employee_time_punch/{record_id}"
    headers = {"Content-Type": "application/json", "Prefer": "transient"}
    ip_address = data.get('ip_address', '').strip()

    print(f"📌 IP Address Provided: '{ip_address}'")

    payload = {}

    # Helper function to add time and IP conditionally
    def add_time_and_ip(time_field, ip_field):
        time_value = data.get(time_field, '').strip()
        if time_value:
            payload[f"custrecord_{time_field}"] = time_value
            if ip_address:
                payload[f"custrecord_{ip_field}"] = ip_address
            print(f"✅ Adding {time_field}: {time_value}, IP: {ip_address}")

    # Apply logic for each field
    add_time_and_ip('punch_in_time', 'punch_in_ip_address')
    add_time_and_ip('break_start_time', 'break_start_ip_address')
    add_time_and_ip('break_end_time', 'break_end_ip_address')
    add_time_and_ip('punch_out_time', 'punch_out_ip_address')

    if not payload:
        print("⚠️ No valid time fields or IP to update. Skipping update.")
        return False

    try:
        response = requests.patch(url, json=payload, headers=headers, auth=auth)
        if response.status_code in [200, 204]:
            print("✅ Punch Record Updated Successfully.")
            return True
        else:
            print(f"❌ NetSuite Update Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Exception during Punch Update: {e}")

    return False


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
        r.headers['Authorization'] = auth_header.replace('OAuth ', f'OAuth realm=\"{self.realm}\",', 1)
        return r
