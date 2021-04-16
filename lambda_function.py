import json
import os

import boto3
import requests
    
from core.utils import send_sms, get_db_data

def lambda_handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['DYNAMO_DB_TABLE']
    table = dynamodb.Table(table_name)
    
    data = get_db_data(db_table=table)

    send_sms()
    
    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }