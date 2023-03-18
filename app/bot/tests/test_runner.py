from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import List, Optional

from app import Session
from app.binance.trade_api import TickerData, Order, SymbolData, TradeApiFilters
from app.bot.models import Trades
from app.bot.runner import PumpDumpBot, BuySellEnum
from config import Config as config


# Define a mock TradeAPI class to test the PumpDumpBot class with
class MockTradeAPI:
    @staticmethod
    def get_symbol_filters() -> TradeApiFilters:
        filters = TradeApiFilters(minPrice="0.00000001", minQuantity="0.001")
        filters.minPrice = "0.00000001"
        filters.minQuantity = "0.001"
        return filters

    @staticmethod
    def get_symbol() -> SymbolData:
        data = SymbolData(price=100.0, symbol="BTCUSDT"

                          )
        data.price = 100.0
        return data

    @staticmethod
    def get_ticker_info() -> TickerData:
        data = TickerData(priceChange="0.00000000", priceChangePercent="0.000", weightedAvgPrice="0.00000000",
                          prevClosePrice="0.00000000", lastPrice="0.00000000", bidPrice="0.00000000",
                          askPrice="0.00000000", openPrice="0.00000000",
                          highPrice="0.00000000", lowPrice="0.00000000", volume="0.00000000", openTime=0, closeTime=0, firstId=0, lastId=0, count=0
                          )
        data.lastPrice = 99.0
        data.priceChangePercent = 1.0
        return data

    @staticmethod
    def get_open_orders() -> Optional[List[Order]]:
        return None  # No open orders


# Define a fixture to replace instances of TradeAPI with MockTradeAPI
@contextmanager
def mock_binance():
    MockTradeAPI


# Define a test class for the PumpDumpBot class
def test_pump_dump_bot():
    # Create an instance of the Session class
    db = Session()

    def test_calculate_buy_price():
        # Create an instance of the PumpDumpBot class
        bot = PumpDumpBot()

        # Mock the TradeAPI class methods to test against specific values
        with mock_binance():
            result = bot.calculate_buy_price("BTCUSDT")

        # Assert that the returned BuyPrice object has the expected values
        assert result.quantity == 0.05050505
        assert result.price == 98.99000000
        assert result.last_price == 99.0

    def test_check_order_status():
        # Create an instance of the PumpDumpBot class
        bot = PumpDumpBot()

        # Mock the TradeAPI.get_order method to return a specific Order object with status="FILLED"
        with mock_binance():
            result = bot.check_order_status("BTCUSDT", BuySellEnum.SELL)

        # Assert that the method returns True
        assert result is True

    def test_check_buy():
        # Create an instance of the PumpDumpBot class
        bot = PumpDumpBot()

        # Mock the TradeAPI.get_open_orders and TradeAPI.client.order_limit_buy methods to test the check_buy method
        with mock_binance():
            bot.check_buy("BTCUSDT")

            # Assert that a new Trades object was added to the database with the expected pair and order_id attributes
            trade = db.query(Trades).filter_by(pair="BTCUSDT").first()
            assert trade is not None
            assert trade.order_id == 1234

    def test_check_sell():
        # Create an instance of the PumpDumpBot class
        bot = PumpDumpBot()

        # Mock the TradeAPI.get_ticker_info, TradeAPI.get_open_orders, and TradeAPI.client.order_limit_sell methods
        # to test the check_sell method
        with mock_binance():
            bot.check_sell("BTCUSDT")

            # Assert that a new Trades object was added to the database with the expected pair and order_id attributes
            trade = db.query(Trades).filter_by(pair="BTCUSDT").first()
            assert trade is not None
            assert trade.order_id == 1234

    def test_run_loop():
        # Create an instance of the PumpDumpBot class
        bot = PumpDumpBot()

        # Mock the TradeAPI.get_open_orders and TradeAPI.get_ticker_info methods to test the run_loop method
        with mock_binance():
            # Use the first symbol in the config file as a test symbol
            symbol = config.symbols[0]

            # Call the run_loop method and let it run for a set amount of time
            with ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.map(bot.run_loop, [symbol])
                for _ in future:
                    pass

            # Assert that a new Trades object was added and then deleted from the database
            trade = db.query(Trades).filter_by(pair=symbol).first()
            assert trade is None

    # Call the test functions
    test_calculate_buy_price()
    test_check_order_status()
    test_check_buy()
    test_check_sell()
    test_run_loop()
