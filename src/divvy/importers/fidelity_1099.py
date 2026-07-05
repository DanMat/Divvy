"""Extract dividend income from a Fidelity Consolidated 1099 PDF.

Best-effort, Fidelity-format-specific: it parses the "Total Ordinary Dividends and
Distributions Detail" supplemental pages. This recovers what you *received* in dividends
(useful as the real-account comparison baseline in a backtest) — it does NOT recover what
you *bought*, so it cannot by itself drive a backtest. Other brokers' 1099 layouts differ;
add a sibling parser for them.

Output schema matches ``divvy.ledger.dividends_actual``: columns ``date, symbol, dividend``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# "ABBVIE INC COM USD0.01, ABBV, 00287Y109"  ->  symbol=ABBV
_HEADER_RE = re.compile(r"^.+,\s*([A-Z][A-Z.]{0,5}),\s*[0-9A-Z]{9}\s*$")
# " 02/14/25 1.57 1.57"  ->  date=02/14/25, first amount = total ordinary dividend
_ROW_RE = re.compile(r"^\s*(\d{2}/\d{2}/\d{2,4})\s+(\d+\.\d+)")


def parse_dividend_text(text: str) -> pd.DataFrame:
    """Parse the flat text of a Fidelity 1099 into a (date, symbol, dividend) table.

    Stops at the "Other Distributions" section so non-dividend (return-of-capital)
    distributions aren't double-counted.
    """
    rows: list[dict] = []
    current_symbol: str | None = None

    for line in text.splitlines():
        if "Other Distributions" in line:
            break
        stripped = line.strip()
        if stripped.startswith(("Subtotals", "TOTALS", "Total ")):
            continue

        header = _HEADER_RE.match(stripped)
        if header:
            current_symbol = header.group(1)
            continue

        row = _ROW_RE.match(line)
        if row and current_symbol:
            date = pd.to_datetime(row.group(1))
            rows.append({"date": date, "symbol": current_symbol, "dividend": float(row.group(2))})

    if not rows:
        return pd.DataFrame(columns=["date", "symbol", "dividend"])
    out = pd.DataFrame(rows)
    return out.groupby(["date", "symbol"], as_index=False)["dividend"].sum().sort_values("date").reset_index(drop=True)


def parse_1099_pdf(path: str | Path) -> pd.DataFrame:
    """Read a Fidelity 1099 PDF and return its dividend detail as (date, symbol, dividend)."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - dependency hint
        raise ImportError("PDF import needs pypdf. Install with: pip install 'divvy-backtest[pdf]'") from exc

    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return parse_dividend_text(text)
