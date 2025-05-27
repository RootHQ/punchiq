import json
import boto3
import os
from datetime import datetime
import pytz

# Initialize resources
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'Punch')
EMPLOYEE_TABLE_NAME = os.environ.get('EMPLOYEE_TABLE', 'employee')

table = dynamodb.Table(TABLE_NAME)
employee_table = dynamodb.Table(EMPLOYEE_TABLE_NAME)

def lambda_handler(event, context):
    print("Received event:", event)
    try:
        body = parse_event_body(event)
        validation_error = validate_body(body)
        if validation_error:
            return build_response(400, {"message": validation_error})

        employee_id = int(body['employeeId'])
        date = body['Date']
        ip_address = body.get('ip_address', '')

        existing_item = get_existing_punch(employee_id, date)
        if existing_item:
            updated_item = build_updated_item(existing_item, body, employee_id, date, ip_address)
            table.put_item(Item=updated_item)
            message_action = "updated"
        else:
            new_item = build_new_item(body, employee_id, date, ip_address)
            table.put_item(Item=new_item)
            message_action = "inserted"

        sqs_message = build_sqs_message(body, employee_id, date, message_action, ip_address)
        SQS_URL = get_setting_value('SQS_URL')
        print("SQS_URL loaded from settings table:", SQS_URL)
        send_sqs_message(SQS_URL, sqs_message)

        return build_response(200, {"message": f"Punch record {message_action} and message sent to SQS."})

    except Exception as e:
        print("Error handling punch record:", e)
        return build_response(500, {"message": "Internal server error"})


def parse_event_body(event):
    return json.loads(event['body']) if 'body' in event else event

def validate_body(body):
    required_fields = ['employeeId', 'Date']
    for field in required_fields:
        if field not in body:
            return f"Missing required field: {field}"
    return None

def get_existing_punch(employee_id, date):
    response = table.scan(
        FilterExpression="employeeId = :employeeId and #date = :date",
        ExpressionAttributeValues={
            ':employeeId': employee_id,
            ':date': date
        },
        ExpressionAttributeNames={
            '#date': 'Date'
        }
    )
    return response['Items'][0] if response['Items'] else None

def build_updated_item(existing_item, body, employee_id, date, ip_address):
    updated_item = existing_item.copy()
    updated_item.update({
        'employeeId': employee_id,
        'companyId': body.get('companyId', existing_item.get('companyId')),
        'netsuiteId': body.get('netsuiteId', existing_item.get('netsuiteId')),
        'Date': date,
    })
    punch_fields = [
        ('punch_in_time', 'custrecord_punch_in_ip_address'),
        ('punch_out_time', 'custrecord_punch_out_ip_address'),
        ('break_start_time', 'custrecord_break_start_ip_address'),
        ('break_end_time', 'custrecord_break_end_ip_address')
    ]
    for time_field, ip_field in punch_fields:
        if body.get(time_field):
            updated_item[time_field] = get_employee_local_time(employee_id)
            updated_item[ip_field] = ip_address
    return updated_item

def build_new_item(body, employee_id, date, ip_address):
    return {
        'employeeId': employee_id,
        'companyId': body.get('companyId', ''),
        'netsuiteId': body.get('netsuiteId', ''),
        'Date': date,
        'punch_in_time': get_employee_local_time(employee_id) if body.get('punch_in_time') else '',
        'punch_out_time': get_employee_local_time(employee_id) if body.get('punch_out_time') else '',
        'break_start_time': get_employee_local_time(employee_id) if body.get('break_start_time') else '',
        'break_end_time': get_employee_local_time(employee_id) if body.get('break_end_time') else '',
        'custrecord_punch_in_ip_address': ip_address if body.get('punch_in_time') else '',
        'custrecord_punch_out_ip_address': ip_address if body.get('punch_out_time') else '',
        'custrecord_break_start_ip_address': ip_address if body.get('break_start_time') else '',
        'custrecord_break_end_ip_address': ip_address if body.get('break_end_time') else ''
    }

def build_sqs_message(body, employee_id, date, message_action, ip_address):
    sqs_message = {
        'employeeId': employee_id,
        'Date': date,
        'action': message_action,
        'ip_address': ip_address
    }
    punch_fields = [
        'punch_in_time',
        'punch_out_time',
        'break_start_time',
        'break_end_time'
    ]
    for field in punch_fields:
        if body.get(field):
            sqs_message[field] = get_employee_local_time(employee_id)
    return sqs_message

def send_sqs_message(SQS_URL, sqs_message):
    sqs.send_message(
        QueueUrl=SQS_URL,
        MessageBody=json.dumps(sqs_message)
    )

def build_response(status, body):
    return {
        "statusCode": status,
        "body": json.dumps(body)
    }

def get_employee_local_time(employee_id):
    try:
        response = employee_table.get_item(Key={'employee_id': employee_id})
        item = response.get('Item', {})
        tz_name = item.get('workplaceTimezone', 'UTC')
        tz = pytz.timezone(tz_name)
        now_local = datetime.now(tz)
        print("Employee local time:", now_local)
        return now_local.strftime("%H:%M")  # Just the time
    except Exception as e:
        print("Error retrieving employee local time:", e)
        return datetime.utcnow().strftime("%H:%M")  # fallback to UTC

def get_setting_value(setting_name):
    try:
        settings_table = dynamodb.Table('setting')
        response = settings_table.get_item(
            Key={'setting_id': setting_name}
        )
        if 'Item' in response:
            return response['Item'].get('value')
        else:
            print(f"Setting {setting_name} not found.")
            return None
    except Exception as e:
        print(f"Error retrieving setting {setting_name}:", e)
        return None
