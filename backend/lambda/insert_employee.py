import json
import boto3
import os

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'employee')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Received event:", event)

    try:
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event  # Para pruebas directas

        required_fields = ['employee_id', 'company_id', 'pin']
        for field in required_fields:
            if field not in body:
                return build_response(400, {"message": f"Missing required field: {field}"})

        active=True
        print(" body['active']",  body['active'])
        if 'active' in body:
            active = body['active']


        item = {
            'employee_id': int(body['employee_id']),
            'company_id': body['company_id'],
            'empName': body.get('empName', ''),
            'empWorkplace': body.get('empWorkplace', ''),
            'pin': body['pin'],
            'active': active,
            'workplaceTimezone': body.get('workplaceTimezone', '')
        }

        table.put_item(Item=item)

        return build_response(200, {"message": "Employee inserted successfully"})

    except Exception as e:
        print("Error inserting employee:", e)
        return build_response(500, {"message": "Internal server error"})

def build_response(status, body):
    return {
        "statusCode": status,
        "body": json.dumps(body)
    }
