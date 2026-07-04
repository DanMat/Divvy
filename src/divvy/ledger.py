"""Parse Fidelity brokerage transaction-history CSVs into normalized events.

A broker-specific parser: it knows Fidelity's `History_for_Account_*.csv`
export format. Other brokers can add a sibling module that produces the same
two outputs (`contributions`, `dividends_actual`) so the rest of the pipeline
stays broker-agnostic.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

_DATE_RE = re.compile(r"^\d{2}-\d{2}-\d{4}$")


def _classify(action: str) -> str:
    if action.startswith("YOU BOUGHT"):
        return "contribution"
    if action.startswith("REINVESTMENT"):
        return "reinvestment"
    if action.startswith("DIVIDEND RECEIVED"):
        return "dividend"
    if action.startswith("YOU SOLD"):
        return "sale"
    if action.startswith("MERGER"):
        return "merger"
    return "other"


def _load_one(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False, on_bad_lines="skip")
    raw = raw[raw["Run Date"].str.match(_DATE_RE, na=False)]
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(raw["Run Date"], format="%m-%d-%Y"),
            "action": raw["Action"].str.strip(),
            "symbol": raw["Symbol"].str.strip(),
            "amount": pd.to_numeric(raw["Amount"], errors="coerce"),
            "quantity": pd.to_numeric(raw["Quantity"], errors="coerce"),
            "price": pd.to_numeric(raw["Price"], errors="coerce"),
        }
    )
    df["event_type"] = df["action"].map(_classify)
    return df


def load_ledger(ledger_dir: str | Path) -> pd.DataFrame:
    """Load and concatenate every Fidelity history CSV in `ledger_dir` into one normalized transaction table."""
    paths = sorted(Path(ledger_dir).glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"No CSV files found in {ledger_dir}")
    df = pd.concat([_load_one(p) for p in paths], ignore_index=True)
    return df.sort_values("date", kind="stable").reset_index(drop=True)


def contributions(df: pd.DataFrame) -> pd.DataFrame:
    """Total new-money $ contributed per date: sum of 'YOU BOUGHT' buys (excludes DRIP reinvestments)."""
    rows = df[df["event_type"] == "contribution"]
    out = rows.groupby("date", as_index=False)["amount"].sum()
    out["amount"] = -out["amount"]  # ledger amounts are negative (cash outflow) -> report as positive $ invested
    return out.rename(columns={"amount": "contributed"}).sort_values("date").reset_index(drop=True)


def dividends_actual(df: pd.DataFrame) -> pd.DataFrame:
    """Actual dividends received per date+symbol, from 'DIVIDEND RECEIVED' rows."""
    rows = df[df["event_type"] == "dividend"]
    out = rows.groupby(["date", "symbol"], as_index=False)["amount"].sum()
    return out.rename(columns={"amount": "dividend"}).sort_values("date").reset_index(drop=True)
