from pathlib import Path

import pandas as pd

from divvy.ledger import contributions, dividends_actual, load_ledger

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_load_ledger_classifies_events_and_skips_footer():
    df = load_ledger(FIXTURE_DIR)
    assert len(df) == 5
    assert list(df["event_type"]) == [
        "contribution",
        "contribution",
        "dividend",
        "reinvestment",
        "sale",
    ]


def test_contributions_sums_new_money_by_date():
    df = load_ledger(FIXTURE_DIR)
    out = contributions(df)
    assert len(out) == 1
    row = out.iloc[0]
    assert row["date"] == pd.Timestamp("2024-01-02")
    assert row["contributed"] == 100.0


def test_dividends_actual_excludes_reinvestment_rows():
    df = load_ledger(FIXTURE_DIR)
    out = dividends_actual(df)
    assert len(out) == 1
    row = out.iloc[0]
    assert row["date"] == pd.Timestamp("2024-02-01")
    assert row["symbol"] == "WID"
    assert row["dividend"] == 1.25
