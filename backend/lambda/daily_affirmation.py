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
        validation_error = validate_required_fields(body, ['employeeId', 'Date'])
        if validation_error:
            return build_response(400, {"message": validation_error})

        employee_id = int(body['employeeId'])
        date = body['Date']
        ip_address = body.get('ip_address', '')

        message_action = handle_punch_record(body, employee_id, date, ip_address)
        sqs_message = build_sqs_message(body, employee_id, date, message_action, ip_address)

        SQS_URL = get_setting_value('SQS_URL')
        print("SQS_URL loaded from settings table:", SQS_URL)
        send_sqs_message(SQS_URL, sqs_message)

        return build_response(200, {"message": f"Punch record {message_action} and message sent to SQS."})

    except Exception as e:
        print("Error handling punch record:", e)
        return build_response(500, {"message": "Internal server error"})


def parse_event_body(event):
    if 'body' in event:
        return json.loads(event['body'])
    return event

def validate_required_fields(body, required_fields):
    for field in required_fields:
        if field not in body:
            return f"Missing required field: {field}"
    return None

def handle_punch_record(body, employee_id, date, ip_address):
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
    if response['Items']:
        updated_item = update_existing_record(response['Items'][0], body, employee_id, date, ip_address)
        table.put_item(Item=updated_item)
        return "updated", updated_item
    else:
        new_item = create_new_record(body, employee_id, date, ip_address)
        table.put_item(Item=new_item)
        return "inserted", new_item

def update_existing_record(existing_item, body, employee_id, date, ip_address):
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

def create_new_record(body, employee_id, date, ip_address):
    punch_fields = [
        ('punch_in_time', 'custrecord_punch_in_ip_address'),
        ('punch_out_time', 'custrecord_punch_out_ip_address'),
        ('break_start_time', 'custrecord_break_start_ip_address'),
        ('break_end_time', 'custrecord_break_end_ip_address')
    ]
    new_item = {
        'employeeId': employee_id,
        'companyId': body.get('companyId', ''),
        'netsuiteId': body.get('netsuiteId', ''),
        'Date': date,
    }
    for time_field, ip_field in punch_fields:
        new_item[time_field] = get_employee_local_time(employee_id) if body.get(time_field) else ''
        new_item[ip_field] = ip_address if body.get(time_field) else ''
    return new_item

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

def send_sqs_message(sqs_url, sqs_message):
    if not sqs_url:
        print("SQS URL is not set. Message not sent.")
        return
    sqs.send_message(
        QueueUrl=sqs_url,
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
