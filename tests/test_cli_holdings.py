import pytest

from divvy.cli import _parse_holdings


def test_parse_holdings_normalizes_percentages():
    w = _parse_holdings("SCHD=45,DGRO=25,VYM=15,SDY=15")
    assert sum(w.values()) == pytest.approx(1.0)
    assert w["SCHD"] == pytest.approx(0.45)


def test_parse_holdings_uppercases_and_sums_dupes():
    w = _parse_holdings("schd=50, schd=50")
    assert w == {"SCHD": 1.0}


def test_parse_holdings_rejects_bad_entry():
    with pytest.raises(SystemExit):
        _parse_holdings("SCHD,VYM")
