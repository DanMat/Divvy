import numpy as np
import pandas as pd

from divvy.engine import run_backtest
from divvy.report import annual_dividends, bucket_nav, risk_metrics


def _md() -> dict[str, pd.DataFrame]:
    idx = pd.to_datetime(["2023-12-29", "2024-06-28", "2024-12-31"])
    return {
        "AAA": pd.DataFrame({"close": [10.0, 12.0, 11.0], "dividend": [0.0, 0.20, 0.20]}, index=idx),
    }


def test_bucket_nav_starts_at_one_and_reflects_total_return():
    nav = bucket_nav({"AAA": 1.0}, _md())
    assert nav.iloc[0] == 1.0
    # Price 10->11 (+10%) plus two $0.20 dividends reinvested -> NAV a bit above 1.10.
    assert nav.iloc[-1] > 1.10


def test_risk_metrics_drawdown_and_vol():
    nav = bucket_nav({"AAA": 1.0}, _md())
    rm = risk_metrics(nav)
    # NAV peaks mid-series (price 12) then falls (price 11) -> negative max drawdown.
    assert rm["max_drawdown_pct"] < 0
    assert rm["annual_vol_pct"] >= 0


def test_risk_metrics_short_series_is_nan():
    rm = risk_metrics(pd.Series([1.0, 1.1]))
    assert np.isnan(rm["max_drawdown_pct"])


def test_annual_dividends_grouped_by_year():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2023-12-29"]), "contributed": [100.0]})
    result = run_backtest(contributions, {"AAA": 1.0}, _md())
    annual = annual_dividends(result)
    # 10 shares bought at $10; both 2024 dividends ($0.20 each on ~10 shares) land in 2024.
    assert 2024 in annual.index
    assert annual.loc[2024] > 0
