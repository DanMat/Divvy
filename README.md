# Divvy

**Replay your real investing history against a *different* portfolio, and compare the dividends and returns you'd have earned.**

Most backtesters (Portfolio Visualizer and friends) simulate a synthetic "$X invested every month." Divvy does that too — but it can also replay your **actual contribution history** (the real dates and dollar amounts you invested, from your broker) into a hypothetical set of holdings, so you can answer:

> *"If I'd put the exact money I actually invested into **this** basket of ETFs/stocks instead, how much more (or less) would I have made — in dividends specifically, and in total?"*

Dividends are reinvested (DRIP) into the same holding, mirroring a real brokerage account, so the comparison compounds the way your account actually does.

---

## Quickstart (no data required)

Backtest a hypothetical "$500/month since 2019" into a couple of dividend baskets:

```bash
uv sync
uv run divvy compare \
  --synthetic-monthly 500 --synthetic-start 2019-01-01 \
  --bucket examples/buckets/dividend_etf_core.yaml \
  --bucket examples/buckets/high_yield_tilt.yaml
```

You'll get a table of total contributed, dividends received, current annual dividend run-rate, ending value, total return, and money-weighted return (XIRR) for each basket — plus charts in `results/<date>/`.

## Bring your own contributions

Any broker can give you a list of what you invested and when. Put it in a two-column CSV:

```csv
date,amount
2021-01-04,200
2021-02-01,200
```

```bash
uv run divvy compare \
  --contributions-csv my_contributions.csv \
  --bucket examples/buckets/dividend_etf_core.yaml
```

See [`examples/contributions.csv`](examples/contributions.csv) for a full sample.

## Define a "bucket" (a candidate portfolio)

A bucket is just a YAML file of tickers and target weights (must sum to 1.0):

```yaml
name: My dividend basket
weights:
  SCHD: 0.50
  VYM: 0.15
  SDY: 0.20
  ABBV: 0.15
```

Drop new buckets in your own `buckets/` folder (gitignored) and pass as many `--bucket` flags as you like to compare them side by side.

## Compare against your *actual* Fidelity account

If you export your Fidelity transaction history CSVs, Divvy can auto-derive both your real contribution calendar **and** the real dividends you received, and add your actual account as a comparison row:

```bash
uv run divvy compare \
  --ledger path/to/fidelity_history_csvs/ \
  --bucket examples/buckets/dividend_etf_core.yaml \
  --real-value 12345.67 --real-as-of 2026-07-03
```

### Import dividends from a Fidelity 1099 (optional)

To reconstruct the dividend income you actually received from a Consolidated 1099 PDF (as a comparison baseline):

```bash
pip install 'divvy[pdf]'
uv run divvy import-1099 --pdf 2025-Consolidated-1099.pdf --out dividends_2025.csv
```

> **Note:** a 1099 records dividends *received*, not what you *bought* — so it can't drive a backtest on its own (that needs your contribution calendar). It's a baseline helper. The parser targets Fidelity's 1099 layout; other brokers differ.

---

## What the numbers mean

| Column | Meaning |
| --- | --- |
| `total_contributed` | Sum of money you put in |
| `total_dividends` | Cumulative dividends received over the whole period (reinvested) |
| `trailing_12mo_dividends` | Dividend income in just the **last year** — your current annual income run-rate |
| `ending_value` | Portfolio value today |
| `total_return_pct` | `(ending_value − contributed) / contributed` |
| `xirr_pct` | Money-weighted annualized return (accounts for contribution timing) |

## Data sources

- **Prices & dividend history:** [yfinance](https://github.com/ranaroussi/yfinance) (free, no key), cached to `data/cache/`.
- **Finviz Elite (optional):** if you have a key, copy `.env.example` to `.env` and add it — used only for ad-hoc yield/screening lookups, **not** required for the core backtest.

## Privacy

Your financial data never leaves your machine and is never committed: `data/`, `results/`, your personal `buckets/`, and `.env` are all gitignored. Only code and the fake `examples/` data live in the repo.

## Install / dev

```bash
uv sync --extra dev   # or: pip install -e '.[dev]'
uv run pytest
```

## Caveats

This is a personal analysis tool, not investment advice. Backtests describe the past; a basket that won over one window can lag in the next. Projections (`divvy.project`) rest on assumptions you choose — treat them as ranges, not predictions.

## License

MIT — see [LICENSE](LICENSE).
