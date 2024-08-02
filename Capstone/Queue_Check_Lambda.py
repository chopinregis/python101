import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('HospitalQueue')

def lambda_handler(event, context):
    hospital = event['hospital']
    
    response = table.query(
        IndexName='HospitalIndex',
        KeyConditionExpression=Key('Hospital').eq(hospital)
    )
    
    return {
        'statusCode': 200,
        'body': {'queueLength': len(response['Items'])}
    }