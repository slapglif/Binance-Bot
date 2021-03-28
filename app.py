import time
import threading
from models import Session, Trades
from trade_api import TradeAPI

db = Session()
trade_api = TradeAPI()


def check_pump():
    """
    Primary market watcher. Creates a threaded loop which uses the
    configured variables to calculate a pump vector and execute a buy
    when the conditions are met. Default configuration is 3% increase in price.
    """
    print("Looking for Buy Opportunities...")
    threading.Thread(target=check_sell).start()
    while True:
        try:
            open_orders = db.query(Trades).all()
            for symbol in trade_api.symbols:
                prices = dict()
                price_action = trade_api.get_price_action(symbol)
                prices[symbol] = '{0:.8f}'.format(round(float(price_action.get('lastPrice')), 8))
                pct_change = float(price_action.get('priceChangePercent'))
                calculation = round(float(prices[symbol]), 8) < float(prices[symbol])*(1 + trade_api.expected_change_buy/100)
                if calculation and pct_change > trade_api.expected_change_buy:
                    current_symbol = symbol
                    if current_symbol not in open_orders:
                        min_price, min_quantity = trade_api.calculate_min(current_symbol)
                        temp_price = float(prices[symbol]) * trade_api.final_buy_price_change
                        final_buy_price = temp_price - (temp_price % float(min_price))
                        temp_quantity = trade_api.buy_quantity_btc / float(final_buy_price)
                        quantity = round((temp_quantity - (temp_quantity % float(min_quantity))), 8)
                        try:
                            trade = Trades.find(symbol)
                            if trade is None:
                                # Place order for buy
                                order = trade_api.client.order_limit_buy(
                                    symbol=current_symbol,
                                    recvWindow=1000,
                                    quantity='{0:.3f}'.format(float(quantity)),
                                    price='{0:.8f}'.format(float(final_buy_price)))
                                print(
                                    f" buy {symbol} at {(float(prices[symbol]) * trade_api.final_buy_price_change)}"
                                    f"from {prices[symbol]} Due to change % {pct_change}"
                                )
                                trade = Trades.get_or_create(symbol)
                                trade.price = str('{0:.8f}'.format(float(prices[symbol])))
                                trade.orderId = order['orderId']
                                trade.quantity = str('{0:.3f}'.format(float(quantity)))
                                db.commit()
                                check_buy_status(symbol)
                        except Exception as e:
                            # print(e)
                            pass
                time.sleep(trade_api.wait_time)
        except Exception as e:
            print(e)

# TODO: Abstract the check_buy and check_sell status to a single method
def check_buy_status(pair):
    try:
        print("Checking status...")
        open_orders = db.query(Trades).filter_by(pair=pair)
        for open_order in open_orders:
            if open_order.pair is not None:
                if open_order.orderId is not None:
                    check = trade_api.client.get_order(
                        symbol=open_order.pair,
                        recvWindow=10000,
                        orderId=open_order.orderId)
                    # Check if order has been filled
                    if check.get('status') == 'FILLED':
                        print(f"Order {open_order.pair} {check.get('status')}")
                        pass
                    else:
                        print(f"{open_order.pair} Not FILLED yet...")
    except Exception as e:
        print(e)


def check_sell_status(pair):
    try:
        print("Checking status...")
        open_orders = db.query(Trades).filter_by(pair=pair)
        for open_sell in open_orders:
            if open_sell.pair and open_sell.orderId:
                    check_sell = trade_api.client.get_order(
                        symbol=open_sell.pair,
                        recvWindow=10000,
                        orderId=open_sell.orderId)
                    # Check if order has been filled
                    if check_sell.get('status') == 'FILLED':
                        print(f"Order {open_sell.pair} {check_sell.get('status')}")
                        db.query(Trades).filter_by(pair=open_sell.pair).delete()
                        db.commit()
                    else:
                        print(f"{open_sell.pair} Not FILLED yet...")
    except Exception as e:
        print(e)


def check_sell():
    print("Looking for Sell Opportunities...")
    max_price = 0
    while True:
        try:
            open_orders = db.query(Trades).all()
            for open_order in open_orders:
                if open_order.price:
                    price_action = trade_api.get_price_action(open_order.pair)
                    current_price = round(float(price_action.get("price")), 8)
                    if current_price > max_price:
                        max_price = float(current_price)
                    if current_price >= float(open_order.price) * (1 + trade_api.expected_change_sell / 100):
                        try:
                            print(f"sell on {open_order.pair} at {open_order.price}, current price is {current_price}")
                            order = trade_api.client.order_limit_sell(
                                symbol=open_order.pair,
                                recvWindow=10000,
                                quantity='{0:.2f}'.format(float(open_order.quantity)),
                                price='{0:.8f}'.format(float(current_price)))
                            open_order.orderId = str(order.get("orderId"))
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
