"""
This module contains the TradeAPI class which is used to interact with the Binance API
"""


from enum import Enum
import logging
from typing import List, Union, Optional, Iterable
from config import Config as config
from binance import Client
from pydantic import BaseModel

logging.basicConfig(
    filename='../../logs/trade_api.log', encoding='utf-8', level=logging.DEBUG
)

logging.info("Loading config...")


class SymbolData(BaseModel):
    """
    Symbol data model for the Binance API
    """
    symbol: str
    price: float


class BinanceResponse(BaseModel):
    """
    Binance response model for the Binance API
    """
    __self__: Union[SymbolData, List[SymbolData]]


class AssetFilterType(Enum):
    """
    Asset filter type enum for the Binance API
    """
    PRICE_FILTER = "PRICE_FILTER"
    LOT_SIZE = "LOT_SIZE"
    MIN_NOTIONAL = "MIN_NOTIONAL"


class AssetFilter(BaseModel):
    """
    Asset filter model for the Binance API
    """
    filterType: str
    minPrice: Optional[str]
    maxPrice: Optional[str]
    tickSize: Optional[str]
    minQty: Optional[str]
    maxQty: Optional[str]
    stepSize: Optional[str]
    minNotional: Optional[str]


class TradeApiFilters(BaseModel):
    """
    Trade API filters model for the Binance API
    """
    minPrice: Optional[str]
    minQuantity: Optional[str]


class AssetInfo(BaseModel):
    """
    Asset info model for the Binance API
    """
    symbol: str
    status: str
    baseAsset: str
    baseAssetPrecision: int
    quoteAsset: str
    quotePrecision: int
    orderTypes: List[str]
    icebergAllowed: bool
    filters: List[AssetFilter]


class TickerData(BaseModel):
    """
    Ticker data model for the Binance API
    """
    priceChange: str
    priceChangePercent: str
    weightedAvgPrice: str
    prevClosePrice: str
    lastPrice: str
    bidPrice: str
    askPrice: str
    openPrice: str
    highPrice: str
    lowPrice: str
    volume: str
    openTime: int
    closeTime: int
    firstId: Optional[int] = None
    lastId: Optional[int] = None
    count: Optional[int] = None


class Order(BaseModel):
    """
    Order model for the Binance API
    """
    symbol: str
    orderId: int
    clientOrderId: str
    price: str
    origQty: str
    executedQty: str
    status: str
    timeInForce: str
    type: str
    side: str
    stopPrice: str
    icebergQty: str
    time: int


class TradeAPI:
    """
    Trade API class for the Binance API
    """

    def __init__(self, is_mock: bool = False):
        """
        The function retrieves data from Binance and transforms the buy price change from 1% to 1.01
        """
        self.client: Client = (
            None if is_mock else Client(config.api_key, config.api_secret)
        )
        # Retrieve data from Binance

    def get_symbol(self, symbol) -> SymbolData:
        """
        this method exists to refresh the symbol data for all symbols, and return
        a given symbol data on request. We do this because we want to ensure that
        our price data always live - at the cost of an extra api call or two.

        :param symbol: The symbol of the instrument you want to trade
        :return: The next symbol data object that matches the symbol passed in.
        """
        symbols_data: List[SymbolData] = self.get_symbols_data()
        return next(filter(lambda x: x.symbol == symbol, symbols_data))

    def get_symbols_data(self) -> List[SymbolData]:
        """
        Gets the symbols data from the client and returns it as a SymbolsData object
        :return: A list of SymbolData objects
        """

        def _generate_symbols() -> Iterable[SymbolData]:
            """
            This function returns an iterable of `SymbolData` objects
            """
            for symbol in config.symbols:
                ticker_info = self.client.get_ticker(symbol=symbol)
                price = ticker_info and ticker_info.get("lastPrice")
                yield SymbolData(symbol=symbol, price=float(price))

        return list(_generate_symbols())

    def get_ticker_info(self, symbol) -> TickerData:
        """
        It returns the ticker info for a given symbol

        :param symbol: The ticker to get the info for
        :type symbol: str
        :return: A TickerData object.
        """
        return self.client.get_ticker(symbol=symbol)

    def get_symbol_filters(self, symbol: str) -> TradeApiFilters:
        """
        It returns the minimum and maximum price for a given symbol

        :param symbol: The symbol to get the filters for
        :type symbol: str
        :return: A tuple of floats.
        """
        symbol_data: Optional[AssetInfo] = self.client.get_symbol_info(symbol)
        if symbol_data is None:
            logging.error(f"Error retrieving data for symbol {symbol}")
        price_filter = next(filter(lambda _filter: _filter.filterType == AssetFilterType.PRICE_FILTER, symbol_data.filters))
        return TradeApiFilters(minPrice=price_filter.minPrice, minQuantity=price_filter.minQty)

    def get_open_orders(self, symbol) -> List[Order]:
        """
        It returns the open orders for the configured symbols
        """
        orders = self.client.get_open_orders(symbol=symbol, recvWindow=10000)
        return [Order(**x) for x in orders]

    def get_order(self, symbol, order_id) -> Order:
        """
        It returns the order for the given symbol and orderId
        """
        order = self.client.get_order(symbol=symbol, orderId=order_id, recvWindow=10000)
        return Order(**order)
