import json
import os

import bitso
import boto3
import requests
    
from core.utils import send_sms, get_db_data

def lambda_handler(event, context):
    
    #Dynamo db init and data
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['DYNAMO_DB_TABLE']
    table = dynamodb.Table(table_name)
    
    data = get_db_data(db_table=table)
    
    #Bitso client
    key = os.environ['BITSO_API_KEY']
    secret = os.environ['BITSO_API_SECRET']

    api = bitso.Api(key, secret)

    status = api.account_status()
    data['daily_limit'] = float(status.daily_limit)
    
    #Trader

    #Send sms monitoring message
    send_sms()
    
    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }