import requests
import os

def get_bitcoin_data(days=21):
    crypto_api_key = os.environ['CRYPTO_API_KEY']
    headers = {
        'authorization': 'Apikey ' + crypto_api_key
    }

    response = requests.get('https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit='+days)

    if response.status_code == 200:
        data = response.json()['Data']['Data']
        data_array = np.array([])
        for i in data:
            data_array = np.append(data_array, i['high'])
        return data_array
    else:
        raise Exception('Data not fetched')

class TraderHandler:
    def __init__(self, initial_amount, btc_price):
        self.data = get_bitcoin_data()

            
