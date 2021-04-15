import json
import requests

def lambda_handler(event, context):
    # TODO implement
    sms_api_key = os.environ['SMS_API_KEY']
    
    headers = {"apikey": sms_api_key}

    data = {
        'message':'Bienvenido a bitgoingAPP, tu código de verificación es: ', 
        'numbers':['5581064181'],
        'country_code':52,
    }

    request = requests.post(url = 'https://api.smsmasivos.com.mx/sms/send', data=data, headers=headers)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }