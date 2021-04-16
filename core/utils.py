import json
import os

import requests


def send_sms():
    '''Sends an sms.'''
    sms_api_key = os.environ['SMS_API_KEY']
    phone_number = os.environ['PHONE_NUMBER']

    headers = {"apikey": sms_api_key}

    data = {
        'message':'Este es un mensaje enviado desde una función lambda :)', 
        'numbers':[phone_number],
        'country_code':52,
    }

    request = requests.post(url = 'https://api.smsmasivos.com.mx/sms/send', data=data, headers=headers)

def get_db_data(db_table):
    '''If data does not exists (first call), we initialize it. '''
    try:
        response = db_table.get_item(Key={
                'key': 1
            })
        data = response['Item']
    except:
        db_table.put_item(Item={
                'key': 1,
                'initial_amount': 100,
                'last_buying_amount': 100,
                'current_amount': 100,
                'current_currency': 'USD',
                'cumulative_earnings': 0,
                'last_moving_average':json.dumps({'long':None, 'short':None})
            })
        response = db_table.get_item(Key={
                'key': 1
            })
        data = response['Item']

    return {
        'initial_amount': float(data['initial_amount']),
        'last_buying_amount': float(data['last_buying_amount']),
        'current_amount': float(data['current_amount']),
        'current_currency': data['current_currency'],
        'cumulative_earnings': float(data['cumulative_earnings']),
        'last_moving_average': json.loads(data['last_moving_average'])
    }