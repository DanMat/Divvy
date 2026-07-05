from divvy.project import (
    future_value,
    monte_carlo_ending_value,
    required_monthly_contribution,
    target_portfolio_value,
)


def test_target_portfolio_value_grosses_up_for_tax_and_yield():
    # $24k/yr after tax at 20% tax -> $30k gross; at 3% yield -> $1,000,000 portfolio.
    target = target_portfolio_value(24_000, 0.20, 0.03)
    assert round(target) == 1_000_000


def test_required_contribution_reaches_target():
    target = 1_000_000
    monthly = required_monthly_contribution(target, current_value=10_000, annual_return=0.08, years=25)
    # Feeding that contribution back through future_value should land ~on target.
    fv = future_value(10_000, monthly, 0.08, 25)
    assert abs(fv - target) < 1.0


def test_monte_carlo_percentiles_are_ordered_and_reproducible():
    mc = monte_carlo_ending_value(10_000, 500, years=20, annual_return_mean=0.08, annual_return_std=0.15, seed=1)
    assert mc["p10"] < mc["p50"] < mc["p90"]
    mc2 = monte_carlo_ending_value(10_000, 500, years=20, annual_return_mean=0.08, annual_return_std=0.15, seed=1)
    assert mc["p50"] == mc2["p50"]  # deterministic with a fixed seed


def test_monte_carlo_zero_volatility_matches_deterministic():
    mc = monte_carlo_ending_value(10_000, 500, years=10, annual_return_mean=0.08, annual_return_std=0.0)
    det = future_value(10_000, 500, 0.08, 10)
    assert abs(mc["p50"] - det) / det < 0.01
