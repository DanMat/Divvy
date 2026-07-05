import pandas as pd

from divvy.engine import run_backtest
from divvy.report import cumulative_dividends, value_over_time


def _market_data() -> dict[str, pd.DataFrame]:
    aaa = pd.DataFrame(
        {"close": [10.0, 11.0], "dividend": [0.0, 0.10]},
        index=pd.to_datetime(["2024-01-02", "2024-02-01"]),
    )
    return {"AAA": aaa}


def test_value_over_time_tracks_holdings():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    result = run_backtest(contributions, {"AAA": 1.0}, _market_data())
    series = value_over_time(result, _market_data())
    # 10 shares bought at $10; on the dividend date value is (10 + DRIP) * $11.
    assert series.iloc[0] == 100.0
    assert series.index[0] == pd.Timestamp("2024-01-02")
    assert series.iloc[-1] > 100.0  # grew with price + DRIP


def test_cumulative_dividends_series():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    result = run_backtest(contributions, {"AAA": 1.0}, _market_data())
    series = cumulative_dividends(result)
    assert series.iloc[-1] == 1.0  # 10 shares * $0.10


def test_cumulative_dividends_unique_index_when_two_tickers_pay_same_day():
    # AAA and BBB both pay a dividend on 2024-02-01 -> index must stay unique.
    same_day = {
        "AAA": pd.DataFrame(
            {"close": [10.0, 11.0], "dividend": [0.0, 0.10]},
            index=pd.to_datetime(["2024-01-02", "2024-02-01"]),
        ),
        "BBB": pd.DataFrame(
            {"close": [20.0, 22.0], "dividend": [0.0, 0.20]},
            index=pd.to_datetime(["2024-01-02", "2024-02-01"]),
        ),
    }
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    result = run_backtest(contributions, {"AAA": 0.5, "BBB": 0.5}, same_day)
    series = cumulative_dividends(result)
    assert series.index.is_unique
