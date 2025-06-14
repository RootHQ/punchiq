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
        body = json.loads(event['body']) if 'body' in event else event

        required_fields = ['employeeId', 'Date']
        for field in required_fields:
            if field not in body:
                return build_response(400, {"message": f"Missing required field: {field}"})

        employee_id = int(body['employeeId'])
        date = body['Date']
        ip_address = body.get('ip_address', '')

        
        # Check if record exists
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

        message_action = ""
        if response['Items']:
            # Update existing record
            existing_item = response['Items'][0]
            updated_item = existing_item.copy()

            updated_item.update({
                'employeeId': employee_id,
                'companyId': body.get('companyId', existing_item.get('companyId')),
                'netsuiteId': body.get('netsuiteId', existing_item.get('netsuiteId')),
                'Date': date,
            })

            if body.get('punch_in_time'):
                updated_item['punch_in_time'] = body.get('punch_in_time')
                updated_item['custrecord_punch_in_ip_address'] = ip_address
            else:
                updated_item['punch_in_time'] =''
                
            if body.get('punch_out_time'):
                updated_item['punch_out_time'] = body.get('punch_out_time')
                updated_item['custrecord_punch_out_ip_address'] = ip_address
            else:
                updated_item['punch_out_time'] =''

            if body.get('break_start_time'):
                updated_item['break_start_time'] = body.get('break_start_time')
                updated_item['custrecord_break_start_ip_address'] = ip_address
            else:
                updated_item['break_start_time'] =''

            if body.get('break_end_time'):
                updated_item['break_end_time'] = body.get('break_end_time')
                updated_item['custrecord_break_end_ip_address'] = ip_address
            else:
                updated_item['break_end_time'] =''

            table.put_item(Item=updated_item)
            message_action = "updated"
        else:
            # Insert new record
            new_item = {
                'employeeId': employee_id,
                'companyId': body.get('companyId', ''),
                'netsuiteId': body.get('netsuiteId', ''),
                'Date': date,
                'punch_in_time':  body.get('punch_in_time') ,
                'punch_out_time':  body.get('punch_out_time') ,
                'break_start_time':  body.get('break_start_time') ,
                'break_end_time':   body.get('break_end_time') ,
                'custrecord_punch_in_ip_address': ip_address if body.get('punch_in_time') else '',
                'custrecord_punch_out_ip_address': ip_address if body.get('punch_out_time') else '',
                'custrecord_break_start_ip_address': ip_address if body.get('break_start_time') else '',
                'custrecord_break_end_ip_address': ip_address if body.get('break_end_time') else ''
            }

            table.put_item(Item=new_item)
            message_action = "inserted"       
       
        return build_response(200, {"message": f"Punch record {message_action}."})

    except Exception as e:
        print("Error handling punch record:", e)
        return build_response(500, {"message": "Internal server error"})

def build_response(status, body):
    return {
        "statusCode": status,
        "body": json.dumps(body)
    }
