# Contributing to Divvy

Thanks for your interest! Divvy is a small, focused tool and contributions are welcome.

## Good first contributions

- **New broker adapters.** The engine only needs a *contribution calendar* (`date, contributed`). Add a parser for your broker's transaction export that produces that schema (see `src/divvy/ledger.py` for the Fidelity example, or just use the generic `--contributions-csv`).
- **More 1099 importers.** `src/divvy/importers/fidelity_1099.py` targets Fidelity's layout. Schwab/Vanguard/etc. parsers that emit `date, symbol, dividend` are welcome.
- **New metrics or report views.**

## Dev setup

```bash
uv sync --extra dev --extra pdf
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Ground rules

- **Never commit personal financial data.** `data/`, `results/`, personal `buckets/`, and `.env` are gitignored — keep it that way. Tests use fake fixtures only.
- CI (ruff + pytest) must pass. Add tests for new behavior.
- Keep the core dependency-light; put heavy/optional deps behind extras (like `[pdf]`).
- Open a PR against `main`; keep changes focused.

## Not investment advice

Divvy is an analysis tool. Please don't add features that present output as recommendations, price targets, or advice.
