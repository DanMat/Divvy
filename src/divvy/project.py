"""Forward projection: how much to invest monthly to reach a future dividend-income goal.

This is a planning model built on assumptions (future total return, portfolio yield,
tax rate), NOT a backtest of what happened. Treat the outputs as ranges, not promises.
"""

from __future__ import annotations

from dataclasses import dataclass


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
