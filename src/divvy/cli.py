"""Command-line interface for Divvy."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from divvy import ledger, market_data, report
from divvy.engine import run_backtest

DEFAULT_START = "2023-11-01"


def _load_bucket(path: Path) -> dict[str, float]:
    return yaml.safe_load(path.read_text())["weights"]


def _parse_year_amount(value: str) -> tuple[int, float]:
    year, amount = value.split("=")
    return int(year), float(amount)


def cmd_compare(args: argparse.Namespace) -> None:
    ledger_dir = Path(args.ledger)
    cache_dir = Path(args.cache_dir)
    out_dir = Path(args.out) / pd.Timestamp.today().strftime("%Y-%m-%d")

    df = ledger.load_ledger(ledger_dir)
    contributions = ledger.contributions(df)
    dividends = ledger.dividends_actual(df)

    variants: dict[str, tuple] = {}
    for bucket_path in args.bucket:
        bucket_path = Path(bucket_path)
        bucket = _load_bucket(bucket_path)
        data = market_data.load_bucket_data(list(bucket), args.start, cache_dir)
        result = run_backtest(contributions, bucket, data)
        variants[bucket_path.stem] = (result, data)

    summary = report.summarize(
        contributions,
        real_dividends_total=float(dividends["dividend"].sum()),
        real_ending_value=args.real_value,
        real_as_of=pd.Timestamp(args.real_as_of),
        bucket_results=variants,
    )

    cross_check = None
    if args.reference_dividends:
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


def main() -> None:
    parser = argparse.ArgumentParser(prog="divvy")
    sub = parser.add_subparsers(dest="command", required=True)

    compare = sub.add_parser("compare", help="Backtest one or more buckets against a real transaction ledger")
    compare.add_argument("--ledger", default="data/raw_ledgers", help="Directory of broker transaction-history CSVs")
    compare.add_argument("--bucket", action="append", required=True, help="Bucket YAML path (repeatable)")
    compare.add_argument("--cache-dir", default="data/cache")
    compare.add_argument("--out", default="results")
    compare.add_argument("--start", default=DEFAULT_START, help="Earliest date to fetch price/dividend history for")
    compare.add_argument("--real-value", type=float, required=True, help="Actual account's current total value")
    compare.add_argument("--real-as-of", required=True, help="Date --real-value was observed (YYYY-MM-DD)")
    compare.add_argument(
        "--reference-dividends",
        action="append",
        metavar="YEAR=AMOUNT",
        help="Known-good yearly dividend total (e.g. from a 1099) to cross-check the parsed ledger against; repeatable",
    )
    compare.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
