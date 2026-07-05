"""Summary report: compare the real ledger against one or more counterfactual buckets."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from divvy.engine import BacktestResult


def _xirr(cashflows: list[tuple[pd.Timestamp, float]], guess: float = 0.1) -> float:
    """Money-weighted annual return for irregularly dated cash flows (Excel XIRR equivalent)."""
    t0 = cashflows[0][0]
    years = np.array([(date - t0).days / 365.0 for date, _ in cashflows])
    amounts = np.array([amount for _, amount in cashflows])

    rate = guess
    for _ in range(100):
        discount = (1 + rate) ** years
        npv = np.sum(amounts / discount)
        dnpv = np.sum(-years * amounts / discount / (1 + rate))
        if abs(dnpv) < 1e-12:
            break
        step = npv / dnpv
        rate -= step
        if abs(step) < 1e-9:
            break
    return rate


def _trailing_dividends_from_history(hist: pd.DataFrame, as_of: pd.Timestamp, months: int = 12) -> float:
    """Dividend income received in the `months` before `as_of`, from a BacktestResult's cumulative history."""
    if hist.empty:
        return 0.0
    window_start = as_of - pd.DateOffset(months=months)
    end = hist[hist["date"] <= as_of]["total_dividends"]
    start = hist[hist["date"] <= window_start]["total_dividends"]
    end_val = float(end.iloc[-1]) if not end.empty else 0.0
    start_val = float(start.iloc[-1]) if not start.empty else 0.0
    return end_val - start_val


def trailing_dividends_from_ledger(dividends_actual: pd.DataFrame, as_of: pd.Timestamp, months: int = 12) -> float:
    """Dividend income actually received in the `months` before `as_of`, from a parsed ledger."""
    window_start = as_of - pd.DateOffset(months=months)
    mask = (dividends_actual["date"] > window_start) & (dividends_actual["date"] <= as_of)
    return float(dividends_actual.loc[mask, "dividend"].sum())


def dividend_cross_check(dividends_actual: pd.DataFrame, reference_totals: dict[int, float]) -> pd.DataFrame:
    """Compare parsed actual-dividend yearly totals against externally supplied reference totals (e.g. 1099s)."""
    by_year = dividends_actual.copy()
    by_year["year"] = by_year["date"].dt.year
    parsed = by_year.groupby("year")["dividend"].sum()

    rows = []
    for year, reference in reference_totals.items():
        parsed_total = float(parsed.get(year, 0.0))
        diff_pct = (parsed_total - reference) / reference * 100 if reference else 0.0
        rows.append(
            {
                "year": year,
                "parsed": round(parsed_total, 2),
                "reference": round(reference, 2),
                "diff_pct": round(diff_pct, 2),
                "flagged": abs(diff_pct) > 1.0,
            }
        )
    return pd.DataFrame(rows)


def summarize(
    contributions: pd.DataFrame,
    bucket_results: dict[str, tuple[BacktestResult, dict[str, pd.DataFrame]]],
    real: tuple[float, float, pd.Timestamp, float] | None = None,
) -> pd.DataFrame:
    """One row per variant: total contributed, dividends received, ending value, return %, XIRR,
    and trailing-12-month dividend income (the current annual income run-rate, vs. the
    cumulative-since-inception `total_dividends` figure).

    `real`, if given, is (real_dividends_total, real_ending_value, real_as_of,
    real_trailing_12mo_dividends) for an actual account to compare against. Omit it for a
    purely synthetic/hypothetical backtest.
    """
    contrib_flows = [(row["date"], -row["contributed"]) for _, row in contributions.iterrows()]
    total_contributed = float(contributions["contributed"].sum())

    rows = []
    if real is not None:
        real_dividends_total, real_ending_value, real_as_of, real_trailing = real
        real_flows = sorted(contrib_flows + [(real_as_of, real_ending_value)])
        rows.append(
            {
                "variant": "Real (actual account)",
                "total_contributed": total_contributed,
                "total_dividends": real_dividends_total,
                "trailing_12mo_dividends": real_trailing,
                "ending_value": real_ending_value,
                "total_return_pct": (real_ending_value - total_contributed) / total_contributed * 100,
                "xirr_pct": _xirr(real_flows) * 100,
            }
        )

    for label, (result, market_data) in bucket_results.items():
        ending_value = result.value(market_data)
        as_of = max(df.index.max() for df in market_data.values())
        flows = sorted(contrib_flows + [(as_of, ending_value)])
        trailing = _trailing_dividends_from_history(result.history_df(), as_of)
        rows.append(
            {
                "variant": label,
                "total_contributed": result.total_contributed,
                "total_dividends": result.total_dividends,
                "trailing_12mo_dividends": trailing,
                "ending_value": ending_value,
                "total_return_pct": (ending_value - result.total_contributed) / result.total_contributed * 100,
                "xirr_pct": _xirr(flows) * 100,
            }
        )

    return pd.DataFrame(rows)


def plot_dividends_over_time(
    real_dividends: pd.DataFrame | None,
    bucket_results: dict[str, BacktestResult],
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))

    if real_dividends is not None:
        real_series = real_dividends.groupby("date")["dividend"].sum().sort_index().cumsum()
        ax.plot(real_series.index, real_series.values, label="Real (actual account)")

    for label, result in bucket_results.items():
        hist = result.history_df()
        div_hist = hist[hist["event"] == "dividend"][["date", "total_dividends"]]
        if not div_hist.empty:
            ax.plot(div_hist["date"], div_hist["total_dividends"], label=label)

    ax.set_title("Cumulative dividends received")
    ax.set_ylabel("$")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_value_over_time(
    bucket_results: dict[str, tuple[BacktestResult, dict[str, pd.DataFrame]]],
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))

    for label, (result, market_data) in bucket_results.items():
        hist = result.history_df()
        snapshots = hist.groupby("date")["shares"].last().sort_index()
        dates, values = [], []
        for date, shares in snapshots.items():
            value = 0.0
            for sym, qty in shares.items():
                if qty <= 0:
                    continue
                prices = market_data[sym]["close"]
                before = prices.index[prices.index <= date]
                price = float(prices.loc[before[-1]]) if len(before) else float(prices.iloc[0])
                value += qty * price
            dates.append(date)
            values.append(value)
        ax.plot(dates, values, label=label)

    ax.set_title("Portfolio value over time")
    ax.set_ylabel("$")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _df_to_markdown(df: pd.DataFrame) -> str:
    header = "| " + " | ".join(df.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows = [
        "| " + " | ".join(f"{v:.2f}" if isinstance(v, float) else str(v) for v in row) + " |"
        for row in df.itertuples(index=False)
    ]
    return "\n".join([header, sep, *rows])


def write_report(out_dir: Path, summary: pd.DataFrame, cross_check: pd.DataFrame | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_dir / "summary.csv", index=False)

    lines = ["# Divvy backtest report", "", "## Summary", _df_to_markdown(summary), ""]
    if cross_check is not None and not cross_check.empty:
        lines += ["## Dividend cross-check vs reference (e.g. 1099s)", _df_to_markdown(cross_check), ""]
    lines += ["![Cumulative dividends](dividends.png)", "![Portfolio value](value.png)"]

    report_path = out_dir / "report.md"
    report_path.write_text("\n".join(lines))
    return report_path
