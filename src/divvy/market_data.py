"""Fetch and cache historical price + dividend data via yfinance."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import yfinance as yf

DEFAULT_CACHE_DIR = Path("data/cache")


def _retry_call(fn, attempts: int = 3, delay: float = 1.5):
    last_exc: Exception | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # yfinance raises assorted exceptions on rate limits/network hiccups
            last_exc = exc
            time.sleep(delay * (attempt + 1))
    raise last_exc


def _fetch(symbol: str, start: str) -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    hist = _retry_call(lambda: ticker.history(start=start, auto_adjust=False, actions=True))
    hist = hist.rename(columns={"Close": "close", "Dividends": "dividend"})[["close", "dividend"]]
    hist.index = hist.index.tz_localize(None).normalize()
    hist.index.name = "date"
    return hist


def load_symbol(symbol: str, start: str, cache_dir: str | Path = DEFAULT_CACHE_DIR) -> pd.DataFrame:
    """Daily close price + per-share dividend (0 on non-ex-dates) for `symbol` from `start`, cached on disk."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{symbol}.parquet"
    if path.exists():
        return pd.read_parquet(path)
    df = _fetch(symbol, start)
    df.to_parquet(path)
    return df


def load_bucket_data(
    symbols: list[str], start: str, cache_dir: str | Path = DEFAULT_CACHE_DIR
) -> dict[str, pd.DataFrame]:
    """Price + dividend history for every symbol in a bucket."""
    return {symbol: load_symbol(symbol, start, cache_dir) for symbol in symbols}
