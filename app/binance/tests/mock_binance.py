import pytest
from typing import List
from app.binance.trade_api import SymbolData, TickerData, AssetFilterType, AssetFilter, AssetInfo, TradeApiFilters, Order


class MockBinanceClient:
    def __init__(self, symbols_data: List[SymbolData], ticker_data: TickerData, symbol_info: AssetInfo, open_orders: List[Order]):
        self.symbols_data = symbols_data
        self.ticker_data = ticker_data
        self.symbol_info = symbol_info
        self.open_orders = open_orders

    def get_ticker(self):
        return {"lastPrice": str(self.ticker_data.lastPrice)}

    def get_symbol_info(self):
        return self.symbol_info

    def get_open_orders(self):
        return [x.dict() for x in self.open_orders]

    def get_order(self, symbol, order_id):
        return next(
            (
                order.dict()
                for order in self.open_orders
                if order.symbol == symbol and order.orderId == order_id
            ),
            None,
        )

    def get_all_tickers(self):
        return [{"symbol": x.symbol, "lastPrice": str(x.price)} for x in self.symbols_data]


@pytest.fixture
def mock_binance_client():
    symbol_data = SymbolData(symbol="LTCBTC", price=0.00358100)
    ticker_data = TickerData(lastPrice="0.00358400", bidPrice="0.00358300", askPrice="0.00358400", openPrice="0.00358400", highPrice="0.00358400", lowPrice="0.00358400",
                             volume="0.00358400", priceChangePercent="0.00358400", weightedAvgPrice="0.00358400",
                             prevClosePrice="0.00358400", openTime=1499827319559,
                             closeTime=1499827319559, firstId=1499827319559, lastId=1499827319559, count=1499827319559, priceChange="0.00358400")
    return MockBinanceClient([symbol_data], ticker_data, None, [])


@pytest.fixture
def mock_open_orders():
    return [
        Order(symbol="LTCBTC", orderId=1, clientOrderId="myOrder1", price="0.1", origQty="1.0", executedQty="0.0", status="NEW", timeInForce="GTC", type="LIMIT", side="BUY",
              stopPrice="0.0", icebergQty="0.0", time=1499827319559),
        Order(symbol="BTCUSDT", orderId=2, clientOrderId="myOrder2", price="50000.0", origQty="2.0", executedQty="1.0", status="FILLED", timeInForce="GTC", type="LIMIT",
              side="SELL",
              stopPrice="0.0", icebergQty="0.0", time=1499827319560)
    ]


@pytest.fixture
def mock_order_list():
    return [
        Order(symbol="LTCBTC", orderId=1, clientOrderId="myOrder1", price="0.1",
              origQty="1.0", executedQty="0.0", status="NEW", timeInForce="GTC", type="LIMIT", side="BUY",
              stopPrice="0.0", icebergQty="0.0", time=1499827319559),
        Order(symbol="BTCUSDT", orderId=2, clientOrderId="myOrder2",
              price="50000.0", origQty="2.0", executedQty="1.0", status="FILLED",
              timeInForce="GTC", type="LIMIT",
              side="SELL",
              stopPrice="0.0", icebergQty="0.0", time=1499827319560)
    ]


@pytest.fixture
def mock_symbol_data():
    return SymbolData(symbol="BTCUSDT", price=55000)


@pytest.fixture
def mock_ticker_data():
    return TickerData(lastPrice="55001", bidPrice="55000", askPrice="55002", closeTime=1610000000000, openTime=1600000000000, openPrice="50000", highPrice="60000"
                      , lowPrice="40000", volume="1000", weightedAvgPrice="55000", prevClosePrice="50000"
                      , priceChangePercent="10.00", priceChange="5000", firstId=1, lastId=1000, count=1000)


@pytest.fixture
def mock_asset_info():
    return AssetInfo(symbol="BTCUSDT", status="TRADING", baseAsset="BTC", baseAssetPrecision=8, quoteAsset="USDT", quotePrecision=8, orderTypes=["LIMIT", "MARKET"],
                     icebergAllowed=False,
                     filters=[AssetFilter(filterType=AssetFilterType.PRICE_FILTER.value, minPrice="0.00000100", maxPrice="100000.00000000", tickSize="0.00000100"),
                              AssetFilter(filterType=AssetFilterType.LOT_SIZE.value, minQty="0.00100000", maxQty="100000.00000000", stepSize="0.00100000"),
                              AssetFilter(filterType=AssetFilterType.MIN_NOTIONAL.value, minNotional="0.00100000")])


@pytest.fixture
def mock_trade_api_filters():
    return TradeApiFilters(minPrice="0.00000100", minQuantity="0.00100000")


@pytest.fixture
def mock_order():
    return Order(symbol="BTCUSDT", orderId=1, clientOrderId="myOrder1", price="55000", origQty="1.0", executedQty="0.0", status="NEW", timeInForce="GTC", type="LIMIT", side="BUY",
                 stopPrice="0.0", icebergQty="0.0", time=1499827319559)
