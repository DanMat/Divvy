import pandas as pd
import pytest

from divvy.engine import run_backtest


def _one_div_md() -> dict[str, pd.DataFrame]:
    idx = pd.to_datetime(["2024-01-02", "2024-02-01"])
    return {"AAA": pd.DataFrame({"close": [10.0, 10.0], "dividend": [0.0, 1.0]}, index=idx)}


def _two_symbol_md() -> dict[str, pd.DataFrame]:
    idx = pd.to_datetime(["2024-01-02", "2025-01-02"])
    return {
        "AAA": pd.DataFrame({"close": [10.0, 20.0], "dividend": [0.0, 0.0]}, index=idx),  # doubles
        "BBB": pd.DataFrame({"close": [10.0, 10.0], "dividend": [0.0, 0.0]}, index=idx),  # flat
    }


def test_dividend_tax_reduces_reinvested_amount():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    taxed = run_backtest(contributions, {"AAA": 1.0}, _one_div_md(), dividend_tax_rate=0.25)
    # 10 shares * $1 = $10 gross dividend; keep $7.50 after 25% tax, reinvested at $10 -> 0.75 shares.
    assert taxed.total_dividends == pytest.approx(10.0)  # gross unchanged
    assert taxed.total_dividends_after_tax == pytest.approx(7.5)
    assert taxed.shares["AAA"] == pytest.approx(10 + 0.75)


def test_default_has_no_tax():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    r = run_backtest(contributions, {"AAA": 1.0}, _one_div_md())
    assert r.total_dividends_after_tax == pytest.approx(r.total_dividends)


def test_expense_ratio_erodes_shares_over_time():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    md = _one_div_md()
    base = run_backtest(contributions, {"AAA": 1.0}, md)
    fee = run_backtest(contributions, {"AAA": 1.0}, md, expense_ratios={"AAA": 0.10})
    # A 10%/yr fee over ~1 month shaves a little off the shares held at the dividend date.
    assert fee.shares["AAA"] < base.shares["AAA"]


def test_rebalance_restores_target_weights():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    md = _two_symbol_md()
    reb = run_backtest(contributions, {"AAA": 0.5, "BBB": 0.5}, md, rebalance="annual")
    # After AAA doubles, a 2025 rebalance restores 50/50 by value at the 2025 prices ($20 / $10).
    val_aaa = reb.shares["AAA"] * 20.0
    val_bbb = reb.shares["BBB"] * 10.0
    assert val_aaa == pytest.approx(val_bbb, rel=1e-6)


def test_rebalance_rejects_bad_freq():
    contributions = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "contributed": [100.0]})
    with pytest.raises(ValueError):
        run_backtest(contributions, {"AAA": 1.0}, _one_div_md(), rebalance="weekly")
