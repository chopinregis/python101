Certainly! I'll guide you through the process of creating an appropriate API Gateway for your hospital queue system project. We'll set this up step-by-step using AWS services.

Step 1: Create a Lambda Function

First, we need to create a Lambda function that will handle the logic for our API.

1. Go to the AWS Lambda console
2. Click "Create function"
3. Choose "Author from scratch"
4. Name your function (e.g., "hospital-queue-handler")
5. Choose Python 3.8 (or later) as the runtime
6. Click "Create function"
7. Replace the default code with the following:

```python
import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HospitalQueue')

def lambda_handler(event, context):
    path = event['path']
    http_method = event['httpMethod']
    
    if path == '/submit' and http_method == 'POST':
        return submit_patient(json.loads(event['body']))
    elif path == '/check_queues' and http_method == 'GET':
        return check_queues()
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Not Found')
        }

def submit_patient(data):
    user_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    item = {
        'UserId': user_id,
        'Name': data['name'],
        'LastName': data['lastName'],
        'DoB': data['dob'],
        'Hospital': data['hospital'],
        'Symptoms': data['symptoms'],
        'Timestamp': timestamp,
        'QueuePosition': calculate_queue_position(data['symptoms'])
    }
    
    table.put_item(Item=item)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'userId': user_id,
            'queuePosition': item['QueuePosition']
        })
    }

def check_queues():
    hospitals = ['Hospital A', 'Hospital B', 'Hospital C']
    queue_lengths = {}
    
    for hospital in hospitals:
        response = table.query(
            IndexName='HospitalIndex',
            KeyConditionExpression=Key('Hospital').eq(hospital)
        )
        queue_lengths[hospital] = len(response['Items'])
    
    return {
        'statusCode': 200,
        'body': json.dumps(queue_lengths)
    }

def calculate_queue_position(symptoms):
    if 'emergency' in symptoms.lower():
        return 1
    return 10  # Default position
```

Step 2: Create a DynamoDB Table

1. Go to the AWS DynamoDB console
2. Click "Create table"
3. Name your table "HospitalQueue"
4. Set the partition key to "UserId" (String)
5. Add a Global Secondary Index:
   - Index name: "HospitalIndex"
   - Partition key: "Hospital" (String)
6. Click "Create"

Step 3: Set Up IAM Role for Lambda

1. Go to the IAM console
2. Click "Roles" in the left sidebar
3. Click "Create role"
4. Select "AWS service" and "Lambda" as the use case
5. Add the following permissions:
   - AWSLambdaBasicExecutionRole
   - AmazonDynamoDBFullAccess (for simplicity; in production, you'd want to limit this)
6. Name the role (e.g., "hospital-queue-lambda-role") and create it
7. Go back to your Lambda function and assign this new role

Step 4: Create the API Gateway

1. Go to the API Gateway console
2. Click "Create API"
3. Choose "REST API" and click "Build"
4. Choose "New API" and name it (e.g., "HospitalQueueAPI")
5. Click "Create API"

Step 5: Create Resources and Methods

1. Click "Actions" and "Create Resource"
2. Name it "submit" and click "Create Resource"
3. With "/submit" selected, click "Actions" and "Create Method"
4. Choose "POST" from the dropdown and click the checkmark
5. Set Integration type to "Lambda Function"
6. Choose your Lambda function and click "Save"
7. Repeat steps 1-6 to create a "GET" method for "/check_queues"

Step 6: Deploy the API

1. Click "Actions" and "Deploy API"
2. Choose "[New Stage]" for deployment stage
3. Name the stage (e.g., "prod") and click "Deploy"
4. Note the "Invoke URL" at the top of the page

Step 7: Update Your EC2 Application

1. SSH into your EC2 instance
2. Edit your `/etc/systemd/system/hospital_queue.service` file:

   ```
   sudo nano /etc/systemd/system/hospital_queue.service
   ```

3. Update the `API_ENDPOINT` environment variable with your new API Gateway URL:

   ```
   Environment="API_ENDPOINT=https://your-api-id.execute-api.your-region.amazonaws.com/prod"
   ```

4. Save the file and exit
5. Reload the systemd daemon and restart your service:

   ```
   sudo systemctl daemon-reload
   sudo systemctl restart hospital_queue
   ```

Step 8: Test Your API

You can now test your API by submitting a form on your web application. The data should be sent to the API Gateway, processed by the Lambda function, stored in DynamoDB, and a response should be sent back to your application.

Remember to handle errors gracefully in your EC2 application, as we discussed in previous responses.

This setup provides a serverless backend for your hospital queue system. The API Gateway handles incoming requests, the Lambda function processes these requests and interacts with DynamoDB, and DynamoDB stores the data persistently.