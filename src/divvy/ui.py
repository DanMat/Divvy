"""Divvy Portfolio Experiment Lab — an interactive local Streamlit app.

Launch with:  divvy ui   (or:  streamlit run src/divvy/ui.py)

Runs entirely on your machine; no financial data leaves the box.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from divvy import contributions as contrib_mod
from divvy import market_data, report, synthetic
from divvy.engine import run_backtest

st.set_page_config(page_title="Divvy · Portfolio Experiment Lab", page_icon="💸", layout="wide")


@st.cache_data(show_spinner=False)
def _load_data(symbols: tuple[str, ...], start: str) -> dict[str, pd.DataFrame]:
    return market_data.load_bucket_data(list(symbols), start)


def _default_bucket(rows: list[tuple[str, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["ticker", "weight"])


def _normalize(df: pd.DataFrame) -> dict[str, float]:
    weights: dict[str, float] = {}
    for _, row in df.iterrows():
        ticker = str(row["ticker"]).strip().upper()
        try:
            weight = float(row["weight"])
        except (TypeError, ValueError):
            continue
        if ticker and weight > 0:
            weights[ticker] = weights.get(ticker, 0.0) + weight
    total = sum(weights.values())
    if total <= 0:
        return {}
    return {sym: w / total for sym, w in weights.items()}


def _contribution_source() -> tuple[pd.DataFrame | None, str | None, str]:
    st.sidebar.header("1 · Contributions")
    mode = st.sidebar.radio(
        "How did you invest?",
        ["Synthetic monthly DCA", "Upload contributions CSV"],
        help="Synthetic = a flat amount every month. CSV = your real dates & amounts (date,amount).",
    )
    if mode == "Synthetic monthly DCA":
        amount = st.sidebar.number_input("Amount per month ($)", min_value=1.0, value=500.0, step=50.0)
        start = st.sidebar.date_input("Start date", value=pd.Timestamp("2019-01-01")).strftime("%Y-%m-%d")
        end = pd.Timestamp.today().strftime("%Y-%m-%d")
        contribs = synthetic.monthly_contributions(start, end, amount)
        return contribs, start, f"${amount:,.0f}/mo since {start}"

    upload = st.sidebar.file_uploader("contributions CSV (date,amount)", type="csv")
    if upload is None:
        return None, None, "awaiting CSV upload"
    contribs = contrib_mod.load_contributions_csv(upload)
    start = contribs["date"].min().strftime("%Y-%m-%d")
    return contribs, start, f"{len(contribs)} contributions from your CSV"


def _bucket_editors() -> dict[str, pd.DataFrame]:
    st.sidebar.header("2 · Portfolios to compare")
    n = st.sidebar.number_input("How many portfolios?", min_value=1, max_value=4, value=2)
    presets = [
        _default_bucket([("SCHD", 0.40), ("DGRO", 0.25), ("VYM", 0.20), ("SDY", 0.15)]),
        _default_bucket([("SCHD", 0.50), ("VYM", 0.15), ("SDY", 0.20), ("ABBV", 0.15)]),
        _default_bucket([("SCHD", 0.40), ("VYM", 0.20), ("SDY", 0.20), ("SPYD", 0.20)]),
        _default_bucket([("SCHD", 0.25), ("DGRO", 0.25), ("VYM", 0.25), ("SDY", 0.25)]),
    ]
    editors: dict[str, pd.DataFrame] = {}
    for i in range(int(n)):
        st.sidebar.subheader(f"Portfolio {chr(65 + i)}")
        edited = st.sidebar.data_editor(
            presets[i],
            num_rows="dynamic",
            key=f"bucket_{i}",
            use_container_width=True,
            column_config={
                "ticker": st.column_config.TextColumn("Ticker"),
                "weight": st.column_config.NumberColumn("Weight", min_value=0.0, step=0.05),
            },
        )
        editors[f"Portfolio {chr(65 + i)}"] = edited
    return editors


def render() -> None:
    st.title("💸 Divvy · Portfolio Experiment Lab")
    st.caption("Replay the same contributions into different portfolios and compare dividends & returns — all locally.")

    contribs, start, source_label = _contribution_source()
    editors = _bucket_editors()

    st.sidebar.header("3 · Run")
    run = st.sidebar.button("▶ Run comparison", type="primary", use_container_width=True)

    st.info(f"**Contributions:** {source_label}")

    if not run:
        st.markdown("Configure your contributions and portfolios in the sidebar, then hit **Run comparison**.")
        _disclaimer()
        return

    if contribs is None or contribs.empty:
        st.error("No contributions to run. Pick synthetic mode or upload a CSV.")
        return

    variants: dict[str, tuple] = {}
    normalized_note: list[str] = []
    with st.spinner("Fetching prices & replaying contributions…"):
        for label, df in editors.items():
            weights = _normalize(df)
            if not weights:
                continue
            try:
                data = _load_data(tuple(sorted(weights)), start)
                result = run_backtest(contribs, weights, data)
            except Exception as exc:  # bad ticker, no data in window, etc.
                st.warning(f"{label}: could not run ({exc}). Check the tickers.")
                continue
            variants[label] = (result, data)
            normalized_note.append(f"**{label}:** " + ", ".join(f"{s} {w:.0%}" for s, w in weights.items()))

    if not variants:
        st.error("No valid portfolios. Add tickers with positive weights.")
        return

    st.caption("Weights normalized to 100%: " + "  ·  ".join(normalized_note))

    summary = report.summarize(contribs, bucket_results=variants)
    _headline_metrics(summary)

    st.subheader("Comparison")
    st.dataframe(
        summary.style.format(
            {
                "total_contributed": "${:,.0f}",
                "total_dividends": "${:,.2f}",
                "trailing_12mo_dividends": "${:,.2f}",
                "ending_value": "${:,.0f}",
                "total_return_pct": "{:.2f}%",
                "xirr_pct": "{:.2f}%",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Portfolio value over time")
        st.line_chart(_combine({k: report.value_over_time(v[0], v[1]) for k, v in variants.items()}))
    with col2:
        st.subheader("Cumulative dividends received")
        st.line_chart(_combine({k: report.cumulative_dividends(v[0]) for k, v in variants.items()}))

    _disclaimer()


def _combine(series_by_label: dict[str, pd.Series]) -> pd.DataFrame:
    deduped = {
        label: series[~series.index.duplicated(keep="last")].sort_index() for label, series in series_by_label.items()
    }
    frame = pd.concat(deduped, axis=1)
    return frame.sort_index().ffill()


def _headline_metrics(summary: pd.DataFrame) -> None:
    best_div = summary.loc[summary["total_dividends"].idxmax()]
    best_ret = summary.loc[summary["total_return_pct"].idxmax()]
    c1, c2, c3 = st.columns(3)
    c1.metric("Most dividends", best_div["variant"], f"${best_div['total_dividends']:,.0f} lifetime")
    c2.metric("Best total return", best_ret["variant"], f"{best_ret['total_return_pct']:.1f}%")
    c3.metric(
        "Top income run-rate",
        summary.loc[summary["trailing_12mo_dividends"].idxmax(), "variant"],
        f"${summary['trailing_12mo_dividends'].max():,.0f}/yr now",
    )


def _disclaimer() -> None:
    st.divider()
    st.warning(
        "⚠️ **Backtest, not advice.** Results describe one past window and don't predict the future. "
        "Past performance is not indicative of future results. Nothing here is personalized financial advice — "
        "do your own research."
    )


if __name__ == "__main__":
    render()
