from app.binance.trade_api import TradeAPI

# instantiate the class
api = TradeAPI()


# test the get_symbol method
def test_get_symbol():
    # test case 1
    symbol = "BTCUSDT"
    expected_result = {"symbol": "BTCUSDT", "price": float}
    assert api.get_symbol(symbol) == expected_result

    # test case 2
    symbol = "ETHBTC"
    expected_result = {"symbol": "ETHBTC", "price": float}
    assert api.get_symbol(symbol) == expected_result


# test the get_symbols_data method
def test_get_symbols_data():
    # test case 1
    expected_result = [{"symbol": str, "price": float}, ...]
    assert api.get_symbols_data() == expected_result


# test the get_ticker_info method
def test_get_ticker_info():
    # test case 1
    symbol = "BTCUSDT"
    expected_result = {"priceChange": str, "priceChangePercent": str, "weightedAvgPrice": str, "prevClosePrice": str, "lastPrice": str, "bidPrice": str, "askPrice": str,
                       "openPrice": str, "highPrice": str, "lowPrice": str, "volume": str, "openTime": int, "closeTime": int, "firstId": None, "lastId": None, "count": None}
    assert api.get_ticker_info(symbol) == expected_result

    # test case 2
    symbol = "ETHBTC"
    expected_result = {"priceChange": str, "priceChangePercent": str, "weightedAvgPrice": str, "prevClosePrice": str, "lastPrice": str, "bidPrice": str, "askPrice": str,
                       "openPrice": str, "highPrice": str, "lowPrice": str, "volume": str, "openTime": int, "closeTime": int, "firstId": None, "lastId": None, "count": None}
    assert api.get_ticker_info(symbol) == expected_result


# test the get_symbol_filters method
def test_get_symbol_filters():
    # test case 1
    symbol = "BTCUSDT"
    expected_result = {"minPrice": str, "minQuantity": str}
    assert api.get_symbol_filters(symbol) == expected_result

    # test case 2
    symbol = "ETHBTC"
    expected_result = {"minPrice": str, "minQuantity": str}
    assert api.get_symbol_filters(symbol) == expected_result


# test the get_open_orders method
def test_get_open_orders():
    # test case 1
    symbol = "BTCUSDT"
    expected_result = [
        {"symbol": str, "orderId": int, "clientOrderId": str, "price": str, "origQty": str, "executedQty": str, "status": str, "timeInForce": str, "type": str, "side": str,
         "stopPrice": str, "icebergQty": str, "time": int}, ...]
    assert api.get_open_orders(symbol) == expected_result

    # test case 2
    symbol = "ETHBTC"
    expected_result = [
        {"symbol": str, "orderId": int, "clientOrderId": str, "price": str, "origQty": str, "executedQty": str, "status": str, "timeInForce": str, "type": str, "side": str,
         "stopPrice": str, "icebergQty": str, "time": int}, ...]
    assert api.get_open_orders(symbol) == expected_result


# test the get_order method
def test_get_order():
    # test case 1
    symbol = "BTCUSDT"
    order_id = 12345678
    expected_result = {"symbol": str, "orderId": int, "clientOrderId": str, "price": str, "origQty": str, "executedQty": str, "status": str, "timeInForce": str, "type": str,
                       "side": str, "stopPrice": str, "icebergQty": str, "time": int}
    assert api.get_order(symbol, order_id) == expected_result

    # test case 2
    symbol = "ETHBTC"
    order_id = 87654321
    expected_result = {"symbol": str, "orderId": int, "clientOrderId": str, "price": str, "origQty": str, "executedQty": str, "status": str, "timeInForce": str, "type": str,
                       "side": str, "stopPrice": str, "icebergQty": str, "time": int}
    assert api.get_order(symbol, order_id) == expected_result
