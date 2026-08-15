from dataclasses import dataclass
import math

import yfinance as yf


@dataclass(frozen=True)
class MarketQuote:
    ticker: str
    price: float
    previous_close: float
    open: float
    high: float
    low: float
    volume: int


def fetch_market_quote(ticker: str) -> MarketQuote:
    symbol = ticker.upper()
    info = yf.Ticker(symbol).fast_info
    values = {
        "price": float(info.last_price),
        "previous_close": float(info.previous_close),
        "open": float(info.open),
        "high": float(info.day_high),
        "low": float(info.day_low),
        "volume": float(info.last_volume),
    }

    if not all(math.isfinite(value) for value in values.values()):
        raise ValueError(f"Incomplete market data for {symbol}")
    if values["previous_close"] == 0:
        raise ValueError(f"Invalid previous close for {symbol}")

    return MarketQuote(
        ticker=symbol,
        price=values["price"],
        previous_close=values["previous_close"],
        open=values["open"],
        high=values["high"],
        low=values["low"],
        volume=int(values["volume"]),
    )
