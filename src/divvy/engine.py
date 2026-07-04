"""Generic event-driven backtest engine: replay a contribution calendar into a portfolio bucket."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


def _price_on_or_after(prices: pd.Series, date: pd.Timestamp) -> tuple[pd.Timestamp, float]:
    """Roll forward to the next trading day on/after `date` present in `prices`."""
    idx = prices.index[prices.index >= date]
    if len(idx) == 0:
        raise ValueError(f"No price data on or after {date.date()}")
    trade_date = idx[0]
    return trade_date, float(prices.loc[trade_date])


@dataclass
class BacktestResult:
    bucket: dict[str, float]
    shares: dict[str, float] = field(default_factory=dict)
    total_contributed: float = 0.0
    total_dividends: float = 0.0
    history: list[dict] = field(default_factory=list)

    def value(self, market_data: dict[str, pd.DataFrame]) -> float:
        """Portfolio value using each symbol's latest available close."""
        return sum(qty * float(market_data[sym]["close"].iloc[-1]) for sym, qty in self.shares.items())

    def history_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.history)


def run_backtest(
    contributions: pd.DataFrame,
    bucket: dict[str, float],
    market_data: dict[str, pd.DataFrame],
) -> BacktestResult:
    """Replay `contributions` (columns: date, contributed) into `bucket` (symbol -> weight).

    Each contribution is split by weight and bought at that date's close (rolled forward to
    the next trading day). Each ex-dividend date for a held symbol pays cash which is
    immediately DRIP'd back into the same symbol, mirroring a real brokerage account.
    """
    total_weight = sum(bucket.values())
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError(f"Bucket weights must sum to 1.0, got {total_weight}")

    result = BacktestResult(bucket=dict(bucket))
    for symbol in bucket:
        result.shares[symbol] = 0.0

    events: list[tuple[pd.Timestamp, int, str, str | None, float]] = []
    for _, row in contributions.iterrows():
        events.append((row["date"], 1, "contribution", None, row["contributed"]))
    for symbol in bucket:
        divs = market_data[symbol]["dividend"]
        for date, per_share in divs[divs > 0].items():
            events.append((date, 0, "dividend", symbol, per_share))
    # Sort chronologically; same-day dividends are settled before that day's contribution,
    # since a same-day buy can't have been held as of the prior ex-dividend record date.
    events.sort(key=lambda e: (e[0], e[1]))

    for date, _, kind, symbol, amount in events:
        if kind == "contribution":
            for sym, weight in bucket.items():
                _, price = _price_on_or_after(market_data[sym]["close"], date)
                result.shares[sym] += (amount * weight) / price
            result.total_contributed += amount
        else:
            shares_held = result.shares[symbol]
            if shares_held <= 0:
                continue
            dividend_amount = shares_held * amount
            result.total_dividends += dividend_amount
            _, price = _price_on_or_after(market_data[symbol]["close"], date)
            result.shares[symbol] += dividend_amount / price

        result.history.append(
            {
                "date": date,
                "event": kind,
                "symbol": symbol,
                "shares": dict(result.shares),
                "total_contributed": result.total_contributed,
                "total_dividends": result.total_dividends,
            }
        )

    return result
