import pandas as pd

from divvy.contributions import load_contributions_csv


def test_load_contributions_csv_flexible_headers(tmp_path):
    csv = tmp_path / "contribs.csv"
    csv.write_text("date,amount\n2024-01-02,100\n2024-02-01,150\n")
    out = load_contributions_csv(csv)
    assert list(out.columns) == ["date", "contributed"]
    assert out["contributed"].tolist() == [100.0, 150.0]
    assert out["date"].tolist() == [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-02-01")]


def test_load_contributions_csv_sums_same_day_and_abs(tmp_path):
    csv = tmp_path / "contribs.csv"
    csv.write_text("date,contributed\n2024-01-02,-50\n2024-01-02,-30\n")
    out = load_contributions_csv(csv)
    assert len(out) == 1
    assert out.iloc[0]["contributed"] == 80.0
