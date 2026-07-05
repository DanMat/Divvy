"""Synthetic contribution schedules, for backtesting hypothetical (non-ledger) DCA scenarios."""

from __future__ import annotations

import pandas as pd


def monthly_contributions(start: str, end: str, amount: float, day: int = 1) -> pd.DataFrame:
    """A flat `amount` contributed on the same day each month from `start` to `end` (inclusive)."""
    dates = pd.date_range(start=start, end=end, freq="MS") + pd.Timedelta(days=day - 1)
    dates = dates[dates <= pd.Timestamp(end)]
    return pd.DataFrame({"date": dates, "contributed": float(amount)})
