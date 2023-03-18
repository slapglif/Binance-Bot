from typing import List

from app.binance.trade_api import SymbolData, TickerData, TradeApiFilters, Order, TradeAPI


# test get_symbol() method
def test_get_symbol_returns_symbol_data(mock_binance_client):
    api = TradeAPI()
    symbol_data = api.get_symbol("LTCBTC")
    assert isinstance(symbol_data, SymbolData)
    assert symbol_data.symbol == "LTCBTC"
    assert symbol_data.price == 0.00358100


def test_get_symbol_returns_none_if_symbol_not_found(mock_binance_client):
    api = TradeAPI()
    symbol_data = api.get_symbol("ETHIC")
    assert symbol_data is None


# test get_symbols_data() method
def test_get_symbols_data_returns_list_of_symbol_data(mock_binance_client):
    api = TradeAPI()
    symbols_data = api.get_symbols_data()
    assert isinstance(symbols_data, List)
    assert all(isinstance(symbol_data, SymbolData) for symbol_data in symbols_data)
    assert symbols_data[0].symbol == "LTCBTC"
    assert symbols_data[0].price == 0.00358100


# test get_ticker_info() method
def test_get_ticker_info_returns_ticker_data(mock_binance_client):
    api = TradeAPI()
    ticker_data = api.get_ticker_info("LTCBTC")
    assert isinstance(ticker_data, TickerData)
    assert ticker_data.lastPrice == "0.00358400"


# test get_symbol_filters() method
def test_get_symbol_filters_returns_trade_api_filters(mock_binance_client):
    api = TradeAPI()
    trade_api_filters = api.get_symbol_filters("LTCBTC")
    assert isinstance(trade_api_filters, TradeApiFilters)
    assert trade_api_filters.minPrice == "0.00000100"
    assert trade_api_filters.minQuantity == "0.00100000"


# test get_open_orders() method
def test_get_open_orders_returns_list_of_orders(mock_binance_client):
    api = TradeAPI()
    orders = api.get_open_orders("LTCBTC")
    assert isinstance(orders, List)
    assert all(isinstance(order, Order) for order in orders)
    assert orders[0].symbol == "LTCBTC"
    assert orders[0].orderId == 1
    assert orders[0].clientOrderId == "myOrder1"
    assert orders[0].price == "0.1"
    assert orders[0].origQty == "1.0"
    assert orders[0].executedQty == "0.0"
    assert orders[0].status == "NEW"
    assert orders[0].timeInForce == "GTC"
    assert orders[0].type == "LIMIT"
    assert orders[0].side == "BUY"
    assert orders[0].stopPrice == "0.0"
    assert orders[0].icebergQty == "0.0"
    assert orders[0].time == 1499827319559


# test get_order() method
def test_get_order_returns_order(mock_binance_client):
    api = TradeAPI()
    order = api.get_order("LTCBTC", 1)
    assert isinstance(order, Order)
    assert order.symbol == "LTCBTC"
    assert order.orderId == 1
    assert order.clientOrderId == "myOrder1"
    assert order.price == "0.1"
    assert order.origQty == "1.0"
    assert order.executedQty == "0.0"
    assert order.status == "NEW"
    assert order.timeInForce == "GTC"
    assert order.type == "LIMIT"
    assert order.side == "BUY"
    assert order.stopPrice == "0.0"
    assert order.icebergQty == "0.0"
    assert order.time == 1499827319559
