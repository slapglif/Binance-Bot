from enum import Enum
import time
import logging
from typing import List, Optional

from pydantic import BaseModel
from config import Config as config
from app.bot.models import Trades
from app.binance.trade_api import TradeAPI, TickerData, Order, SymbolData, TradeApiFilters
from concurrent.futures import ThreadPoolExecutor
import sys
from app import Session

logging.basicConfig(filename='../../logs/app.log', encoding='utf-8', level=logging.DEBUG)

# using pytest we need to test these functions, we have a mock fixture in app.binance.tests.mock_binance


trade_api = TradeAPI(is_mock=True)
db = Session()


def handle_error(e):
    """
    `handle_error` is a function that takes an error as an argument and logs the error to the console

    :param e: The exception object
    """
    logging.error(f'Error on line {sys.exc_info()[-1].tb_lineno}\n{type(e).__name__, e}')


class BuyPrice(BaseModel):
    """
    Buy price model for the application
    """

    quantity: float
    price: float
    last_price: float


class BuySellEnum(Enum):
    """
    BuySellEnum enum for the application
    """

    BUY = "buy"
    SELL = "sell"


class PumpDumpBot:
    """
    PnDBot class for the application
    """

    @classmethod
    def calculate_buy_price(cls, symbol: str) -> BuyPrice:
        """
        If the current price is less than or equal to the expected price with
        expected_increase_percent, and the price change is greater than expected_increase_percent,
        and the symbol is not already in open orders, then calculate the minimum price
        and quantity, calculate the final buy price using final_buy_price_change_percent,
        and calculate the quantity to buy
        :return: BuyPrice(quantity=quantity, price=final_buy_price, last_price=last_price)
        """

        def _run_calculation(_last_price) -> BuyPrice:
            """
            Calculate the quantity and price to buy based on the last price and the symbol filters

            :param _last_price: The last price of the symbol
            :return: The quantity, price, and last_price are being returned.
            """
            # Calculate the minimum price and quantity
            filters: TradeApiFilters = trade_api.get_symbol_filters(symbol)

            # Calculate the final buy price using final_buy_price_change_percent
            symbol_data: SymbolData = trade_api.get_symbol(symbol)
            temp_price = _last_price * symbol_data.price / 100
            final_buy_price = temp_price - (temp_price % float(filters.minPrice))

            # Calculate the quantity to buy
            temp_quantity = config.buy_quantity_btc / float(final_buy_price)
            quantity = round((temp_quantity - (temp_quantity % float(filters.minQuantity))), 8)
            return BuyPrice(quantity=quantity, price=final_buy_price, last_price=_last_price)

        # Get the current price and price change
        price_action: TickerData = trade_api.get_ticker_info(symbol)
        last_price = float(price_action.lastPrice)
        price_change_percent = float(price_action.priceChangePercent)

        # Calculate the expected increase using expected_increase_percent
        expected_increase = last_price * config.expected_change_buy / 100

        if last_price <= expected_increase and price_change_percent > config.expected_change_buy:
            # Check if the symbol is already in open orders
            return _run_calculation(symbol)

    @classmethod
    def check_buy(cls, symbol):
        """
        Check for buy opportunities and place a buy order if the price is below the buy price

        :param cls: This is the class itself
        :param symbol: The symbol you want to buy
        """
        logging.info("Looking for Buy Opportunities...")

        # Get all the open orders from database
        open_trade = db.session.query(Order).filter_by(symbol=symbol).first()
        if open_trade and cls.check_order_status(symbol, BuySellEnum.BUY):
            logging.info(f"Already have an open order for {symbol}, skipping...")
            return

        # Get all open orders from the exchange
        open_orders: Optional[List[Order]] = trade_api.get_open_orders(symbol)
        if not open_orders and not open_trade:
            # Calculate the buy price
            buy_data: BuyPrice = cls.calculate_buy_price(symbol)

            # Place an order to buy
            _order = trade_api.client.order_limit_buy(
                symbol=symbol,
                recvWindow=1000,
                quantity="{0:.3f}".format(float(buy_data.quantity)),
                price="{0:.8f}".format(float(buy_data.price))
            )

            logging.info(f"Buy {symbol} at {buy_data.price} from {buy_data.last_price}")

            # Add the order to the database
            db.add(Trades(pair=symbol, order_id=_order["orderId"]))
            db.commit()

    @classmethod
    def check_sell(cls, symbol: str):
        """
        If the current price is greater than the price of the
        order by the expected change, then sell the order

        :param cls: This is the class that the method is being called from
        :param symbol: The symbol of the coin you want to trade
        :type symbol: str
        """
        logging.info("Looking for Sell Opportunities...")

        # Get all the open orders from database
        open_trades = db.query(Trades).filter_by(symbol=symbol).all()
        order_status = cls.check_order_status(symbol, BuySellEnum.SELL)

        # Check if the symbol is already in open orders
        if open_trades and order_status:
            logging.info(f"Already have an open sell order for {symbol}, skipping...")
            return

        # Get the latest price action for the symbol
        price_action: TickerData = trade_api.get_ticker_info(symbol)
        open_orders: List[Order] = trade_api.get_open_orders(symbol)

        # Check if the current price is greater than the price of the order by the expected change
        for order in open_orders:
            last_price = float(price_action.lastPrice)

            # Check if the current price is greater than the price of the order by the expected change
            if last_price >= float(order.price) * (1 + config.expected_change_sell / 100):
                logging.info(f"sell on {order.symbol} at {order.price}, current price is {last_price}")

                # Place an order to sell
                _order = trade_api.client.order_limit_sell(
                    symbol=order.symbol,
                    recvWindow=10000,
                    quantity="{0:.2f}".format(float(order.executedQty)),
                    price="{0:.8f}".format(last_price),
                )

    @classmethod
    def check_order_status(cls, symbol: str, side: BuySellEnum):
        """
        Check if the order has been filled, if it has, delete the order from the database

        :param cls: The class that the method is bound to
        :param symbol: The symbol of the asset you want to trade
        :type symbol: str
        :param side: BuySellEnum.BUY or BuySellEnum.SELL
        :type side: str
        """
        try:
            logging.info("Checking status...")

            # Get all the open orders from database
            open_orders = db.query(Trades).filter_by(symbol=symbol).all()

            # Check if the symbol is already in open orders
            for order in open_orders:
                order: Order = trade_api.get_order(symbol=order.symbol, order_id=order.orderId)

                # Check if the order has been filled
                if order.status == "FILLED":
                    logging.info(f"Order {order.symbol} {order.status}")

                    # Delete the order from the database
                    if side == BuySellEnum.SELL:
                        db.query(Trades).filter_by(pair=order.symbol).delete()
                        db.commit()
                        logging.info(f"Deleted {order.symbol} from database")
                        return True
                logging.info(f"{order.symbol} Not FILLED yet...")
        except Exception as e:
            handle_error(e)

    @classmethod
    def run_loop(cls, symbol: str):
        """
        It loops through the symbols in the config file and checks if the conditions for buying are met

        :param cls: the class that the method is in
        :param symbol: The symbol of the asset you want to trade
        """
        while True:
            try:
                cls.check_buy(symbol)
                cls.check_sell(symbol)
            except Exception as e:
                handle_error(e)
            time.sleep(config.wait_time)


