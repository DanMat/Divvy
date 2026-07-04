import pandas as pd
import pytest

from divvy.engine import run_backtest


def _market_data() -> dict[str, pd.DataFrame]:
    aaa = pd.DataFrame(
        {"close": [10.0, 11.0], "dividend": [0.0, 0.10]},
        index=pd.to_datetime(["2024-01-02", "2024-02-01"]),
    )
    bbb = pd.DataFrame(
        {"close": [20.0], "dividend": [0.0]},
        index=pd.to_datetime(["2024-01-02"]),
    )
    return {"AAA": aaa, "BBB": bbb}


def test_run_backtest_contribution_and_drip():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    bucket = {"AAA": 0.5, "BBB": 0.5}

    result = run_backtest(contributions, bucket, _market_data())

    # $50 into AAA at $10/share = 5 shares; $50 into BBB at $20/share = 2.5 shares.
    assert result.total_contributed == 100.0
    assert result.shares["BBB"] == pytest.approx(2.5)

    # Dividend on 2024-02-01: 5 shares held * $0.10 = $0.50, DRIP'd back into AAA at $11/share.
    assert result.total_dividends == pytest.approx(0.50)
    assert result.shares["AAA"] == pytest.approx(5 + 0.50 / 11)


def test_run_backtest_rejects_bad_weights():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    with pytest.raises(ValueError):
        run_backtest(contributions, {"AAA": 0.5, "BBB": 0.4}, _market_data())
