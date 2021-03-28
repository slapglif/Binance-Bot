from binance.client import Client
from collections import namedtuple
from typing import Tuple
import requests
import json


class TradeAPI:

    def __init__(self):
        config = json.load(open('config.json'), object_hook=lambda d: namedtuple('config', d.keys())(*d.values()))
        self.client: callable = Client(config.api_key, config.api_secret)
        self.wait_time = config.wait_time
        # Percentage to add to current price when buying
        self.buy_price_change = config.buy_price_change
        # TODO: Make this dynamic based on ATR
        # Quantity to buy converted from Bitcoin
        self.buy_quantity_btc = config.buy_quantity_btc
        # Necessary change before placing a order
        self.expected_change_buy = config.expected_change_buy
        # Expected profit
        self.expected_change_sell = config.expected_change_sell
        # Transform 1% to 1.01
        self.final_buy_price_change = config.final_buy_price_change + self.buy_price_change / 100
        # Retrieve data from Binance
        try:
            self.ticker_data = requests.get(config.ticker_api).json()
            self.exchange_data = requests.get(config.exchange_api).json()
        except Exception as e:
            print(e)
            print("Exiting program due to api error...")
            exit()
        if len(config.symbols) < 1:
            self.symbols = [self.ticker_data[ticker].get('symbol') for ticker in range(len(self.ticker_data)) if "BTC" in self.ticker_data[ticker].get('symbol')]
        self.symbol_data = self.exchange_data.get('symbols')

    @staticmethod
    def get_price_action(symbol: str) -> dict:
        response = requests.get(f"https://api.binance.com/api/v1/ticker/24hr?symbol={symbol}")
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(e)

    def calculate_min(self, symbol) -> Tuple[int, float]:
        min_price = 0
        min_quantity = 0
        for ticker in self.symbol_data:
            if ticker.get('symbol') == symbol:
                filters = ticker.get('filters')
                if filters and len(filters) > 1:
                    min_price = float(filters[0].get('tickSize'))
                    min_quantity = float(filters[2].get('stepSize'))
        return min_price, min_quantity
