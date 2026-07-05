"""Template for a new broker adapter — copy this to add Schwab / Vanguard / etc.

The backtest engine only needs a **contribution calendar**: a DataFrame with columns
``date`` and ``contributed`` (positive dollars invested). Optionally, you can also expose the
**dividends actually received** as ``date, symbol, dividend`` for the real-account comparison row.

To add a broker:
1. Copy this file to e.g. ``schwab.py``.
2. Implement ``contributions()`` (and optionally ``dividends_actual()``) to parse that broker's
   export into the schemas below. See ``divvy/ledger.py`` for a complete Fidelity example.
3. Add a test with a small fixture (fake data only — never commit real statements).

Output schemas (must match exactly so the rest of the pipeline stays broker-agnostic):
    contributions      -> columns: date (datetime64), contributed (float, positive $)
    dividends_actual   -> columns: date (datetime64), symbol (str), dividend (float $)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load(path: str | Path) -> pd.DataFrame:
    """Load and normalize this broker's raw export into one transaction table.

    Replace the body with real parsing. Keep the column names generic so the derivations below
    can be broker-agnostic where possible.
    """
    raise NotImplementedError("Implement the broker-specific parser here (see divvy/ledger.py).")


def contributions(df: pd.DataFrame) -> pd.DataFrame:
    """Return new-money contributions as (date, contributed). Exclude dividend reinvestments."""
    raise NotImplementedError


def dividends_actual(df: pd.DataFrame) -> pd.DataFrame:
    """Optional: dividends received as (date, symbol, dividend) for the real-account comparison."""
    raise NotImplementedError
