from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Config:
    """
    Config class for the application
    """
    api_key: str = getenv("API_KEY")
    api_secret: str = getenv("API_SECRET")
    wait_time: int = getenv("WAIT_TIME")
    buy_price_chang: int = getenv("BUY_PRICE_CHANGE")
    buy_quantity_btc: float = getenv("BUY_QUANTITY_BTC")
    expected_change_buy: float = getenv("EXPECTED_CHANGE_BUY")
    expected_change_sell: float = getenv("EXPECTED_CHANGE_SELL")
    symbols: list = getenv("SYMBOLS")
