import uuid
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HospitalQueue')

def lambda_handler(event, body):
    user_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Process and store user data
    item = {
        'UserId': user_id,
        'Name': body['name'],
        'LastName': body['lastName'],
        'DoB': body['dob'],
        'Hospital': body['hospital'],
        'Symptoms': body['symptoms'],
        'Timestamp': timestamp,
        'QueuePosition': calculate_queue_position(body['symptoms'])
    }
    
    table.put_item(Item=item)
    
    return {
        'statusCode': 200,
        'body': {'userId': user_id, 'queuePosition': item['QueuePosition']}
    }

def calculate_queue_position(symptoms):
    # Implement your queue position logic here
    # This is a simplistic example
    if 'emergency' in symptoms.lower():
        return 1
    return 10  # Default position