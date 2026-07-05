import pandas as pd

from divvy.importers.fidelity_1099 import parse_dividend_text

# Synthetic text modeled on Fidelity's "Total Ordinary Dividends and Distributions Detail".
SAMPLE = """\
Total Ordinary Dividends and Distributions Detail
ABBVIE INC COM USD0.01, ABBV, 00287Y109
 02/14/25 1.57 1.57
 05/15/25 1.63 1.63
Subtotals 3.20 3.20
SCHWAB US DIVIDEND EQUITY ETF, SCHD, 808524797
 03/31/25 2.80 0.05 2.75
 06/30/25 3.21 0.05 3.16
Subtotals 6.01 0.10 5.91
TOTALS 9.21
Other Distributions, Tax and Expense Detail
REALTY INCOME CORP COM, O, 756109104
 01/15/25 0.05
"""


def test_parse_dividend_text_extracts_symbol_date_amount():
    out = parse_dividend_text(SAMPLE)
    assert set(out["symbol"]) == {"ABBV", "SCHD"}
    abbv = out[out["symbol"] == "ABBV"]
    assert abbv["dividend"].sum() == 3.20
    schd = out[out["symbol"] == "SCHD"]
    # First numeric after each date is the total ordinary dividend.
    assert schd["dividend"].tolist() == [2.80, 3.21]


def test_parse_dividend_text_stops_before_other_distributions():
    # The Realty Income row lives under "Other Distributions" and must be excluded.
    out = parse_dividend_text(SAMPLE)
    assert "O" not in set(out["symbol"])


def test_parse_dividend_text_dates_parsed():
    out = parse_dividend_text(SAMPLE)
    assert out["date"].min() == pd.Timestamp("2025-02-14")
