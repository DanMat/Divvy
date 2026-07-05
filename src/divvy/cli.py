"""Command-line interface for Divvy."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from divvy import contributions as contrib_mod
from divvy import ledger, market_data, report, synthetic
from divvy.engine import run_backtest

DEFAULT_START = "2023-11-01"


def _load_bucket(path: Path) -> dict[str, float]:
    return yaml.safe_load(path.read_text())["weights"]


def _parse_year_amount(value: str) -> tuple[int, float]:
    year, amount = value.split("=")
    return int(year), float(amount)


def cmd_compare(args: argparse.Namespace) -> None:
    sources = [bool(args.ledger), bool(args.synthetic_monthly), bool(args.contributions_csv)]
    if sum(sources) > 1:
        raise SystemExit("Pass only one of --ledger, --synthetic-monthly, --contributions-csv")

    cache_dir = Path(args.cache_dir)
    out_dir = Path(args.out) / pd.Timestamp.today().strftime("%Y-%m-%d")

    dividends = None
    real = None
    if args.ledger:
        df = ledger.load_ledger(Path(args.ledger))
        contributions = ledger.contributions(df)
        dividends = ledger.dividends_actual(df)
        if args.real_value is not None:
            real_as_of = pd.Timestamp(args.real_as_of)
            real_trailing = report.trailing_dividends_from_ledger(dividends, real_as_of)
            real = (float(dividends["dividend"].sum()), args.real_value, real_as_of, real_trailing)
        history_start = args.start
    elif args.synthetic_monthly:
        end = args.synthetic_end or pd.Timestamp.today().strftime("%Y-%m-%d")
        contributions = synthetic.monthly_contributions(args.synthetic_start, end, args.synthetic_monthly)
        history_start = args.synthetic_start
    elif args.contributions_csv:
        contributions = contrib_mod.load_contributions_csv(args.contributions_csv)
        history_start = contributions["date"].min().strftime("%Y-%m-%d")
    else:
        raise SystemExit("Provide a contribution source: --ledger, --synthetic-monthly, or --contributions-csv")

    variants: dict[str, tuple] = {}
    for bucket_path in args.bucket:
        bucket_path = Path(bucket_path)
        bucket = {sym: w for sym, w in _load_bucket(bucket_path).items() if w > 0}
        data = market_data.load_bucket_data(list(bucket), history_start, cache_dir)
        result = run_backtest(contributions, bucket, data)
        variants[bucket_path.stem] = (result, data)

    summary = report.summarize(contributions, bucket_results=variants, real=real)

    cross_check = None
    if dividends is not None and args.reference_dividends:
        reference_totals = dict(_parse_year_amount(v) for v in args.reference_dividends)
        cross_check = report.dividend_cross_check(dividends, reference_totals)

    out_dir.mkdir(parents=True, exist_ok=True)
    report.plot_dividends_over_time(dividends, {k: v[0] for k, v in variants.items()}, out_dir / "dividends.png")
    report.plot_value_over_time(variants, out_dir / "value.png")
    report_path = report.write_report(out_dir, summary, cross_check)

    print(summary.to_string(index=False))
    if cross_check is not None:
        print("\nDividend cross-check:")
        print(cross_check.to_string(index=False))
    print(f"\nReport written to {report_path}")


def cmd_import_1099(args: argparse.Namespace) -> None:
    from divvy.importers import fidelity_1099

    dividends = fidelity_1099.parse_1099_pdf(args.pdf)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    dividends.to_csv(args.out, index=False)
    by_year = dividends.assign(year=dividends["date"].dt.year).groupby("year")["dividend"].sum()
    print(f"Parsed {len(dividends)} dividend rows -> {args.out}")
    print("Total dividends by year:")
    print(by_year.round(2).to_string())


def cmd_ui(args: argparse.Namespace) -> None:
    import importlib.util
    import subprocess
    import sys

    if importlib.util.find_spec("streamlit") is None:
        raise SystemExit("The UI needs Streamlit. Install it with: pip install 'divvy[ui]'")

    ui_path = importlib.util.find_spec("divvy.ui").origin
    cmd = [sys.executable, "-m", "streamlit", "run", ui_path]
    if args.port:
        cmd += ["--server.port", str(args.port)]
    subprocess.run(cmd, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(prog="divvy")
    sub = parser.add_subparsers(dest="command", required=True)

    compare = sub.add_parser(
        "compare", help="Backtest one or more buckets against a real ledger or a synthetic contribution schedule"
    )
    compare.add_argument(
        "--ledger", help="Directory of Fidelity transaction-history CSVs (auto-derives contributions + real dividends)"
    )
    compare.add_argument("--contributions-csv", help="Generic date,amount CSV of your contributions (any broker)")
    compare.add_argument("--synthetic-monthly", type=float, help="Flat $ amount contributed monthly (no data needed)")
    compare.add_argument("--synthetic-start", help="Start date for --synthetic-monthly (YYYY-MM-DD)")
    compare.add_argument("--synthetic-end", help="End date for --synthetic-monthly (default: today)")
    compare.add_argument("--bucket", action="append", required=True, help="Bucket YAML path (repeatable)")
    compare.add_argument("--cache-dir", default="data/cache")
    compare.add_argument("--out", default="results")
    compare.add_argument(
        "--start", default=DEFAULT_START, help="Earliest date to fetch price/dividend history for (--ledger mode)"
    )
    compare.add_argument("--real-value", type=float, help="Actual account's current total value (--ledger mode)")
    compare.add_argument("--real-as-of", help="Date --real-value was observed, YYYY-MM-DD (--ledger mode)")
    compare.add_argument(
        "--reference-dividends",
        action="append",
        metavar="YEAR=AMOUNT",
        help="Known-good yearly dividend total (e.g. from a 1099) to cross-check the parsed ledger against; repeatable",
    )
    compare.set_defaults(func=cmd_compare)

    imp = sub.add_parser("import-1099", help="Extract dividend income from a Fidelity 1099 PDF into a CSV")
    imp.add_argument("--pdf", required=True, help="Path to a Fidelity Consolidated 1099 PDF")
    imp.add_argument("--out", required=True, help="Output CSV path (date,symbol,dividend)")
    imp.set_defaults(func=cmd_import_1099)

    ui = sub.add_parser("ui", help="Launch the interactive Portfolio Experiment Lab in your browser")
    ui.add_argument("--port", type=int, help="Port for the local Streamlit server (optional)")
    ui.set_defaults(func=cmd_ui)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
