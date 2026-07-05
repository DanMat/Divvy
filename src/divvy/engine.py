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
    total_dividends_after_tax: float = 0.0
    history: list[dict] = field(default_factory=list)

    def value(self, market_data: dict[str, pd.DataFrame]) -> float:
        """Portfolio value using each symbol's latest available close."""
        return sum(qty * float(market_data[sym]["close"].iloc[-1]) for sym, qty in self.shares.items())

    def history_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.history)


_REBALANCE_FREQ = {"annual": "YS", "quarterly": "QS", "monthly": "MS"}


def run_backtest(
    contributions: pd.DataFrame,
    bucket: dict[str, float],
    market_data: dict[str, pd.DataFrame],
    *,
    dividend_tax_rate: float = 0.0,
    expense_ratios: dict[str, float] | None = None,
    rebalance: str | None = None,
) -> BacktestResult:
    """Replay `contributions` (columns: date, contributed) into `bucket` (symbol -> weight).

    Each contribution is split by weight and bought at that date's close (rolled forward to
    the next trading day). Each ex-dividend date for a held symbol pays cash which is
    immediately DRIP'd back into the same symbol, mirroring a real brokerage account.

    Optional realism (all default to the original behavior):
    - `dividend_tax_rate`: taxes each dividend and reinvests only the after-tax amount, as in a
      taxable account. `total_dividends` stays gross; `total_dividends_after_tax` is what's kept.
    - `expense_ratios`: annual fund fee per symbol (e.g. {"SCHD": 0.0006}), applied as a
      continuous share haircut over elapsed time.
    - `rebalance`: "annual" / "quarterly" / "monthly" — reset holdings to target weights at each
      period boundary. Default None leaves DRIP to drift.
    """
    total_weight = sum(bucket.values())
    if abs(total_weight - 1.0) > 1e-6:
        raise ValueError(f"Bucket weights must sum to 1.0, got {total_weight}")
    if rebalance is not None and rebalance not in _REBALANCE_FREQ:
        raise ValueError(f"rebalance must be one of {sorted(_REBALANCE_FREQ)} or None, got {rebalance!r}")
    expense_ratios = expense_ratios or {}

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
    if rebalance is not None and events:
        span_start = min(e[0] for e in events)
        # The portfolio lives until the last available price, past the final contribution/dividend.
        span_end = max(max(e[0] for e in events), max(md.index.max() for md in market_data.values()))
        for reb_date in pd.date_range(span_start, span_end, freq=_REBALANCE_FREQ[rebalance]):
            if reb_date > span_start:
                events.append((reb_date, 2, "rebalance", None, 0.0))
    # Sort chronologically; same-day dividends settle first (a same-day buy can't have been held
    # as of the prior ex-dividend record date), then contributions, then any rebalance.
    events.sort(key=lambda e: (e[0], e[1]))

    last_date: pd.Timestamp | None = None
    for date, _, kind, symbol, amount in events:
        # Continuous expense-ratio drag for the elapsed time since the previous event.
        if expense_ratios and last_date is not None and date > last_date:
            years = (date - last_date).days / 365.0
            for sym, er in expense_ratios.items():
                if er and result.shares.get(sym, 0.0) > 0:
                    result.shares[sym] *= (1.0 - er) ** years
        last_date = date

        if kind == "contribution":
            for sym, weight in bucket.items():
                _, price = _price_on_or_after(market_data[sym]["close"], date)
                result.shares[sym] += (amount * weight) / price
            result.total_contributed += amount
        elif kind == "rebalance":
            held_value = 0.0
            prices: dict[str, float] = {}
            for sym in bucket:
                _, prices[sym] = _price_on_or_after(market_data[sym]["close"], date)
                held_value += result.shares[sym] * prices[sym]
            if held_value > 0:
                for sym, weight in bucket.items():
                    result.shares[sym] = held_value * weight / prices[sym]
        else:
            shares_held = result.shares[symbol]
            if shares_held <= 0:
                continue
            gross = shares_held * amount
            net = gross * (1.0 - dividend_tax_rate)
            result.total_dividends += gross
            result.total_dividends_after_tax += net
            _, price = _price_on_or_after(market_data[symbol]["close"], date)
            result.shares[symbol] += net / price  # reinvest what's kept after tax

        result.history.append(
            {
                "date": date,
                "event": kind,
                "symbol": symbol,
                "shares": dict(result.shares),
                "total_contributed": result.total_contributed,
                "total_dividends": result.total_dividends,
                "total_dividends_after_tax": result.total_dividends_after_tax,
            }
        )

    return result
