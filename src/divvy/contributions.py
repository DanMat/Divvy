"""Broker-agnostic contribution calendar loader.

A contribution calendar is the input the backtest engine actually needs: the dates and
dollar amounts you invested. Anyone can produce this from any broker as a simple two-column
CSV, without a broker-specific transaction parser.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

_DATE_ALIASES = ("date", "run date", "run_date", "day")
_AMOUNT_ALIASES = ("contributed", "amount", "invested", "contribution")


def _pick(columns: list[str], aliases: tuple[str, ...]) -> str:
    lower = {c.lower().strip(): c for c in columns}
    for alias in aliases:
        if alias in lower:
            return lower[alias]
    raise ValueError(f"CSV must have one of columns {aliases}; got {columns}")


def load_contributions_csv(path: str | Path) -> pd.DataFrame:
    """Load a generic contributions CSV into the engine's schema (columns: date, contributed).

    Accepts flexible header names (e.g. date/run date, amount/contributed/invested) and
    treats amounts as positive dollars invested. Multiple rows on the same date are summed.
    """
    raw = pd.read_csv(path)
    date_col = _pick(list(raw.columns), _DATE_ALIASES)
    amount_col = _pick(list(raw.columns), _AMOUNT_ALIASES)

    out = pd.DataFrame(
        {
            "date": pd.to_datetime(raw[date_col]),
            "contributed": pd.to_numeric(raw[amount_col], errors="coerce").abs(),
        }
    )
    out = out.dropna(subset=["contributed"])
    out = out.groupby("date", as_index=False)["contributed"].sum()
    return out.sort_values("date").reset_index(drop=True)
