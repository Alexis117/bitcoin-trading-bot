import os

import requests
import numpy as np


def get_bitcoin_data(days=21):
    crypto_api_key = os.environ['CRYPTO_API_KEY']
    headers = {
        'authorization': 'Apikey ' + crypto_api_key
    }

    response = requests.get('https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit='+str(days))

    if response.status_code == 200:
        data = response.json()['Data']['Data']
        data_array = np.array([])
        for i in data:
            data_array = np.append(data_array, i['close'])
        return data_array
    else:
        raise Exception('Bitcoin data not fetched')

class TraderBot:
    def __init__(self, db_data, bitso_client):
        self.bitcoin_data = get_bitcoin_data()
        self.current_currency = db_data['current_currency']
        self.last_moving_average = db_data['last_moving_average']
        self.initial_amount = db_data['initial_amount']
        self.current_amount = db_data['current_amount']
        self.last_buying_amount = db_data['last_buying_amount']
        self.cumulative_earnings = db_data['cumulative_earnings']
        self.bitso_client = bitso_client
            
    def run(self):
        if not self.last_moving_average['long']: #Check if first call and initializing
            self.last_moving_average['long'] = self.calculate_moving_average(av_type='long')
            self.last_moving_average['short'] = self.calculate_moving_average(av_type='short')
        
        moving_average = {}
        moving_average['long'] = self.calculate_moving_average(av_type='long')
        moving_average['short'] = self.calculate_moving_average(av_type='short')

        action = self.decide_action(moving_average = moving_average)

        self.last_moving_average['long'] = moving_average['long']
        self.last_moving_average['short'] = moving_average['short']

        new_db_data = {
            'last_buying_amount': self.last_buying_amount,
            'current_amount': self.current_amount,
            'current_currency': self.current_currency,
            'cumulative_earnings': self.cumulative_earnings,
            'last_moving_average': self.last_moving_average
        }

        return {'action':action, 'new_db_data':new_db_data}
    
    def calculate_moving_average(self, av_type):
        short_values = self.bitcoin_data[len(self.bitcoin_data)-1-9:len(self.bitcoin_data)]
        long_values = self.bitcoin_data
        if av_type == 'short':
            moving_average = sum(short_values)/len(short_values)
        elif av_type == 'long':
            moving_average = sum(long_values)/len(long_values)
        return moving_average
    
    def decide_action(self, moving_average):
        btc_buy_price, btc_sell_price = self.get_current_bitso_prices()

        if self.current_currency == 'BTC':
            #Selling with 10% earnings rule
            if self.current_amount * btc_buy_price > 1.05 * self.last_buying_amount:
                if self.current_amount * btc_buy_price * 0.9935 > self.initial_amount:
                    self.cumulative_earnings = self.cumulative_earnings + ( self.current_amount * btc_buy_price * 0.9935 ) - self.initial_amount
                    self.current_amount = self.initial_amount
                else:
                    self.current_amount = self.current_amount * self_buy_price * 0.9935
                self.current_currency = 'USD'
                return {'action':'SELL', 'message':'Earnings taken'}

        #Bull tendency case
        if moving_average['long'] > moving_average['short']:
            if self.last_moving_average['long'] < self.last_moving_average['short']:
                if self.current_currency == 'USD':
                    self.current_amount = ( self.current_amount * 0.9935 ) / btc_sell_price
                    self.current_currency = 'BTC'
                    return {'action':'BUY', 'message':'Tendency is up'}
            else:
                return {'action':'NONE', 'message':'Tendency is the same'}
        #Bear tendency case
        else:
            if self.last_moving_average['long'] > self.last_moving_average['short']:
                if self.current_currency == 'BTC':
                    if self.current_amount * btc_buy_price * 0.9935 > self.initial_amount:
                        self.cumulative_earnings = self.cumulative_earnings + ( self.current_amount * btc_buy_price * 0.9935 ) - self.initial_amount
                        self.current_amount = self.initial_amount
                    else:
                        self.current_amount = self.current_amount * btc_buy_price * 0.9935
                    self.current_currency = 'USD'
                    return {'action':'SELL', 'message':'Tendency is down'}
            else:
                return {'action':'NONE', 'message':'Tendency is the same'}

    def get_current_bitso_prices(self):
        trades = self.bitso_client.trades('btc_mxn')
        last_sell = None
        last_buy = None
        for trade in trades:
            if not last_sell:
                if trade.maker_side == 'sell':
                    last_sell = trade
            if not last_buy:
                if trade.maker_side == 'buy':
                    last_buy = trade
            if last_sell and last_buy:
                break
        return last_buy, last_sell