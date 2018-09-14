from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import requests
import time
import threading
import json
from models import Session, Trade

# Replace your_api_key, your_api_secret with your api_key, api_secret
client = Client("your_api_key",
                "your_api_secret")


#The api for prices
api = "https://api.binance.com/api/v3/ticker/price"
#The api for minimum price and minimum quantity
api1 = "https://api.binance.com//api/v1/exchangeInfo"
data = requests.get(api).json()  # Retrieve data from Binance
data1 = requests.get(api1).json()  # Retrieve data from Binance
data1 = data1['symbols']  # Filter data from data1

symbols = []  # The list of symbols

wait_time = 5  # Number of seconds to wait before repeating the while loop
buy_price_change = 3  # Percentage to add to current price when buying
buy_quantity_btc = 0.0022  # Quantity to buy converted from Bitcoin
expected_change_buy = 2   # Necessary change before placing a order
expected_change_sell = 10  # Expected profit
tolerance = 1  # Tolerance from max price
final_buy_price_change = 1 + buy_price_change/100  # Transform 1% to 1.01


prices = {}

db = Session()


for x in range(len(data)):
    if("BTC" in data[x]['symbol']): # Create list with cryptocurrencies that we can buy with BTC
        symbols.append(data[x]['symbol'])


def calculate_min(symbol):
    for x in data1:
        if(x['symbol'] == symbol):
            min_price = float(x['filters'][0]['tickSize'])
            minQty = float(x['filters'][1]['stepSize'])
    return min_price,minQty


def check_pump():
    print("Looking for Buy Opportunities...")
    threading.Thread(target=check_sell).start()
    while True:
        try:
            open_orders = db.query(Trade).all()
            for symbol in symbols:
                r2 = requests.get("https://api.binance.com/api/v1/ticker/24hr?symbol=" + symbol).json()
                prices[symbol] = '{0:.8f}'.format(round(float(r2['lastPrice']), 8))
                pct_change = float(r2['priceChangePercent'])
                if round(float(prices[symbol]), 8) < float(prices[symbol])*(1 + expected_change_buy/100) \
                        and pct_change > expected_change_buy:
                    # print(pct_change, expected_change_buy)
                    current_symbol = symbol
                    if current_symbol not in open_orders:
                        min_price, min_Qty = calculate_min(current_symbol)
                        temp_price = float(prices[symbol]) * final_buy_price_change
                        final_buy_price = temp_price - (temp_price % float(min_price))
                        temp_quantity = buy_quantity_btc / float(final_buy_price)
                        quantity = round((temp_quantity - ((temp_quantity % float(min_Qty)))), 8)
                        try:
                            trade = Trade.find(symbol)
                            if trade is None:
                                order = client.order_limit_buy(  # Place order for buy
                                    symbol=current_symbol,
                                    recvWindow=1000,
                                    quantity='{0:.3f}'.format(float(quantity)),
                                    price='{0:.8f}'.format(float(final_buy_price)))
                                print("Buy: " + symbol + ' at: ' + str('{0:.8f}'.format(float(prices[symbol])
                                * final_buy_price_change)) + " from " +
                                      str(prices[symbol]) + " Due to change % " + str(pct_change))
                                trade = Trade.get_or_create(symbol)
                                trade.price = str('{0:.8f}'.format(float(prices[symbol])))
                                trade.orderId = order['orderId']
                                trade.quantity = str('{0:.3f}'.format(float(quantity)))
                                db.commit()
                                check_buy_status(symbol)
                            else:
                                continue
                        except Exception as e:
                            # print(e)
                            pass
                time.sleep(5)

        except Exception as e:
            print(e)


def check_buy_status(pair):
    try:
        print("Checking status...")
        open_orders = db.query(Trade).filter_by(pair=pair)
        for open_order in open_orders:
            if open_order.pair is not None:
                if open_order.orderId is not None:
                    check = client.get_order(
                        symbol=open_order.pair,
                        recvWindow=10000,
                        orderId=open_order.orderId)
                    if check['status'] == 'FILLED':  # Check if order has been filled
                        print("Order " + open_order.pair + " " + check['status'])  # print order status
                        pass
                    else:
                        print(open_order.pair + " Not FILLED yet...")
    except Exception as e:
        print(e)


def check_sell_status(pair):
    try:
        print("Checking status...")
        open_orders = db.query(Trade).filter_by(pair=pair)
        for open_sell in open_orders:
            if open_sell.pair is not None:
                if open_sell.orderId is not None:
                    check_sell = client.get_order(
                        symbol=open_sell.pair,
                        recvWindow=10000,
                        orderId=open_sell.orderId)
                    if check_sell['status'] == 'FILLED':  # Check if order has been filled
                        print("Order " + open_sell.pair + " " + check_sell['status'])
                        db.query(Trade).filter_by(pair=open_sell.pair).delete()
                        db.commit()
                    else:
                        print(open_sell.pair + " Not FILLED yet...")
    except Exception as e:
        print(e)


def check_sell():
    print("Looking for Sell Opportunities...")
    max_price = 0
    while True:
        try:
            # print("Check Sell...")
            open_orders = db.query(Trade).all()
            for open_order in open_orders:
                if open_order.price is not None:
                    r = requests.get("https://api.binance.com/api/v1/ticker/price?symbol=" + open_order.pair).json()
                    current_price = round(float(r['price']), 8)
                    if (current_price > max_price):
                        max_price = float(current_price)

                    if current_price >= float(open_order.price) * (1 + expected_change_sell / 100):
                        try:
                            print("sell on " + open_order + " at " + open_order.price +
                                  " current price is " + str(current_price))
                            order = client.order_limit_sell(
                                symbol=open_order.pair,
                                recvWindow=10000,
                                quantity='{0:.2f}'.format(float(open_order.quantity)),
                                price='{0:.8f}'.format(float(current_price)))
                            open_order.orderId = str(order['orderId'])
                            db.commit()
                            check_sell_status(open_order.pair)
                        except Exception as e:
                            print(e)
        except Exception as e:
            print(e)
        time.sleep(5)


def main():
    threading.Thread(target=check_pump).start()


if __name__ == '__main__':
    main()
