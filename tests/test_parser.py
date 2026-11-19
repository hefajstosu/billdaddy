from datetime import date
from decimal import Decimal

from app.ocr.parser import parse

BIEDRONKA = """Jeronimo Martins Polska S.A.
BIEDRONKA nr 1234
Kraków ul. Długa 5
2026-11-02 nr wydr.1234
PARAGON FISKALNY
ML.ŁACIATE 3,2% 1L 2 x3,49 6,98C
CZEK.MILKA ALPEJSKA (1 x5,99 5,99A
PAPIER TOAL.FOXY 8R 1 x14,99 14,99A
BANANY LUZ 0,856 x5,99 S5,13C
CHLEB ŻYTNI 500G 1 x4,29 4,29C
SUMA PLN 37,38
"""


def test_header():
    r = parse(BIEDRONKA)
    assert r["shop"] == "Biedronka"
    assert r["date"] == date(2026, 11, 2)
    assert r["total"] == Decimal("37.38")


def test_items():
    items = parse(BIEDRONKA)["items"]
    assert len(items) == 5
    assert items[0] == {
        "raw_name": "ML.ŁACIATE 3,2% 1L",
        "price": Decimal("3.49"),
        "quantity": Decimal("2"),
    }
    # ocr garbage around numbers
    assert items[1]["raw_name"] == "CZEK.MILKA ALPEJSKA"
    assert items[3]["quantity"] == Decimal("0.856")


def test_suma_is_not_item():
    names = [i["raw_name"] for i in parse(BIEDRONKA)["items"]]
    assert not any("SUMA" in n for n in names)


def test_line_without_qty():
    r = parse("TORBA FOLIOWA 0,99A")
    assert r["items"][0]["price"] == Decimal("0.99")
    assert r["items"][0]["quantity"] == 1


def test_other_date_format_and_bad_date():
    assert parse("LIDL\n16.11.2026 12:01")["date"] == date(2026, 11, 16)
    assert parse("LIDL\n2026-13-45")["date"] is None


def test_unknown_shop():
    assert parse("SKLEP U ZDZISIA\nCHLEB 4,29C")["shop"] is None
