"""Forward projection: how much to invest monthly to reach a future dividend-income goal.

This is a planning model built on assumptions (future total return, portfolio yield,
tax rate), NOT a backtest of what happened. Treat the outputs as ranges, not promises.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def target_portfolio_value(
    annual_income_after_tax: float,
    tax_rate: float,
    portfolio_yield: float,
) -> float:
    """Portfolio value needed to throw off `annual_income_after_tax` in dividends.

    Assumes dividends grow with the portfolio, so yield-on-market-value stays ~constant.
    """
    gross_needed = annual_income_after_tax / (1 - tax_rate)
    return gross_needed / portfolio_yield


def required_monthly_contribution(
    target_value: float,
    current_value: float,
    annual_return: float,
    years: int,
) -> float:
    """Monthly contribution needed to grow `current_value` to `target_value` over `years`.

    `annual_return` is total return (price appreciation + reinvested dividends), compounded
    monthly. DRIP is assumed throughout accumulation.
    """
    i = annual_return / 12
    n = years * 12
    growth = (1 + i) ** n
    fv_of_current = current_value * growth
    remaining = target_value - fv_of_current
    if remaining <= 0:
        return 0.0
    annuity_factor = (growth - 1) / i
    return remaining / annuity_factor


def future_value(
    current_value: float,
    monthly_contribution: float,
    annual_return: float,
    years: int,
) -> float:
    """Projected portfolio value from a fixed monthly contribution (monthly compounding, DRIP)."""
    i = annual_return / 12
    n = years * 12
    growth = (1 + i) ** n
    return current_value * growth + monthly_contribution * (growth - 1) / i


@dataclass
class ProjectionInputs:
    annual_income_after_tax: float
    tax_rate: float
    portfolio_yield: float
    current_value: float
    horizons: tuple[int, ...] = (20, 25)
    returns: tuple[float, ...] = (0.07, 0.08, 0.09)


def sensitivity_grid(inp: ProjectionInputs) -> list[dict]:
    """Required monthly contribution across a grid of horizons x assumed returns."""
    target = target_portfolio_value(inp.annual_income_after_tax, inp.tax_rate, inp.portfolio_yield)
    rows = []
    for years in inp.horizons:
        row = {"years": years, "target_value": round(target)}
        for r in inp.returns:
            row[f"return_{int(r * 100)}pct"] = round(required_monthly_contribution(target, inp.current_value, r, years))
        rows.append(row)
    return rows


def monte_carlo_ending_value(
    current_value: float,
    monthly_contribution: float,
    years: int,
    annual_return_mean: float,
    annual_return_std: float,
    n_sims: int = 10_000,
    seed: int | None = 42,
) -> dict[str, float]:
    """Distribution of ending portfolio values when monthly returns are random, not fixed.

    Draws monthly returns from a normal distribution (mean = annual_return_mean/12,
    sd = annual_return_std/sqrt(12)) so the deterministic single-number projection becomes a
    range. Returns percentiles (p10/p25/p50/p75/p90) and the mean of the ending value.
    """
    rng = np.random.default_rng(seed)
    months = years * 12
    monthly_mean = annual_return_mean / 12.0
    monthly_std = annual_return_std / (12.0**0.5)

    draws = rng.normal(monthly_mean, monthly_std, size=(n_sims, months))
    value = np.full(n_sims, float(current_value))
    for m in range(months):
        value = value * (1.0 + draws[:, m]) + monthly_contribution
    pct = np.percentile(value, [10, 25, 50, 75, 90])
    return {
        "p10": float(pct[0]),
        "p25": float(pct[1]),
        "p50": float(pct[2]),
        "p75": float(pct[3]),
        "p90": float(pct[4]),
        "mean": float(value.mean()),
    }
