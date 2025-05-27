import json
import boto3
import os

# Inicializa el recurso de DynamoDB
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

        if 'employee_id' not in body:
            return build_response(400, {"message": "Missing required field: employee_id"})

        employee_id = int(body['employee_id'])

        # Ejecuta la eliminación
        table.delete_item(
            Key={'employee_id': employee_id}
        )

        return build_response(200, {"message": "Employee deleted successfully"})

    except Exception as e:
        print("Error deleting employee:", e)
        return build_response(500, {"message": "Internal server error"})

def build_response(status, body):
    return {
        "statusCode": status,
        "body": json.dumps(body)
    }
