import boto3
import json
import os

# FIX 1: The client must be 'sagemaker-runtime', not the endpoint name
runtime_client = boto3.client('sagemaker-runtime')

# FIX 2: Use an Environment Variable or paste the actual Endpoint Name here
ENDPOINT_NAME = "sagemaker-xgboost-2026-03-24-04-12-06-***" 

def lambda_handler(event, context):
    try:
        # Handle API Gateway / Postman body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
            
        features = body.get('features')
            
        if not features:
            return {
                "statusCode": 400, 
                "body": json.dumps({"error": "No 'features' list found in JSON body"})
            }

        # Convert list [8450, 7, ...] to CSV string "8450,7,..."
        csv_payload = ",".join(map(str, features))

        # Send to SageMaker
        response = runtime_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='text/csv',
            Body=csv_payload
        )
        
        # FIX 3: Regression models return a single price value
        result = response['Body'].read().decode('utf-8')
        predicted_price = float(result)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'estimated_sale_price': predicted_price,
                'status': 'success'
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
