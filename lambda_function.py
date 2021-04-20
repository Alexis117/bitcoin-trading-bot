import json
import os

import bitso
import boto3
import requests
    
from core.utils import send_sms, get_db_data
from core.trading import TraderBot

def lambda_handler(event, context):
    
    #Dynamo db init and data
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['DYNAMO_DB_TABLE']
    table = dynamodb.Table(table_name)
    
    data = get_db_data(db_table=table)
    
    #Bitso client
    key = os.environ['BITSO_API_KEY']
    secret = os.environ['BITSO_API_SECRET']

    bitso_client = bitso.Api(key, secret)

    #Trader
    result = TraderBot(db_data=data, bitso_client=bitso_client).run()

    if result['action']['action'] != 'NONE':
        update_data = result['data']
        data = update_db_data(db_table=table, data=update_data)

    #Send sms monitoring message
    send_sms(info=result)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'data':data, 'action':action})
    }