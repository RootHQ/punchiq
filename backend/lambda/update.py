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
            body = event 

        required_fields = ['employee_id', 'company_id', 'pin']
        for field in required_fields:
            if field not in body:
                return build_response(400, {"message": f"Missing required field: {field}"})

        employee_id = int(body['employee_id'])

        update_expression = "SET company_id = :company_id, pin = :pin"
        expression_values = {
            ':company_id': body['company_id'],
            ':pin': body['pin']
        }

        if 'empName' in body:
            update_expression += ", empName = :empName"
            expression_values[':empName'] = body['empName']
        if 'empWorkplace' in body:
            update_expression += ", empWorkplace = :empWorkplace"
            expression_values[':empWorkplace'] = body['empWorkplace']
        if 'workplaceTimezone' in body:
            update_expression += ", workplaceTimezone = :workplaceTimezone"
            expression_values[':workplaceTimezone'] = body['workplaceTimezone']

        table.update_item(
            Key={'employee_id': employee_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )

        return build_response(200, {"message": "Employee updated successfully"})

    except Exception as e:
        print("Error updating employee:", e)
        return build_response(500, {"message": "Internal server error"})

def build_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }
