import re
from datetime import date
from decimal import Decimal

# NAME  qty x unit_price  total + PTU letter
# ocr sometimes adds garbage like "(1" or "S5,13C" so regex is a bit loose
QTY_RE = re.compile(
    r"^(?P<name>.+?)\s+\(?(?P<qty>\d+(?:[.,]\d+)?)[A-Za-z]?\s*[xX*]\s*"
    r"(?P<unit>\d+[.,]\d{2})\s+\S*?(?P<total>\d+[.,]\d{2})\S*$"
)
# NAME ...  price + PTU letter at the end
ITEM_RE = re.compile(r"^(?P<name>.+?)\s+(?P<price>\d+[.,]\d{2})\s*[A-G]?$")
TOTAL_RE = re.compile(r"SUMA\s*(?:PLN)?\s*:?\s*(?P<total>\d+[.,]\d{2})", re.I)
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})|(\d{2})[.-](\d{2})[.-](\d{4})")

SHOPS = {
    "biedronka": "Biedronka",
    "jeronimo": "Biedronka",
    "lidl": "Lidl",
    "kaufland": "Kaufland",
    "auchan": "Auchan",
    "carrefour": "Carrefour",
    "zabka": "Żabka",
    "żabka": "Żabka",
    "rossmann": "Rossmann",
    "dino": "Dino",
    "netto": "Netto",
}

# lines that look like items but aren't
SKIP_WORDS = (
    "SUMA",
    "PTU",
    "RESZTA",
    "GOTÓWKA",
    "GOTOWKA",
    "KARTA",
    "RABAT",
    "SPRZEDAŻ",
    "SPRZEDAZ",
)


def to_num(s):
    return Decimal(s.replace(",", ".").replace(" ", ""))


def find_shop(lines):
    for line in lines[:5]:
        low = line.lower()
        for key, name in SHOPS.items():
            if key in low:
                return name
    return None


def find_date(text):
    m = DATE_RE.search(text)
    if not m:
        return None
    if m.group(1):
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return date(int(m.group(6)), int(m.group(5)), int(m.group(4)))


def parse(text):
    lines = [s.strip() for s in text.splitlines() if s.strip()]
    result = {
        "shop": find_shop(lines),
        "date": None,
        "total": None,
        "items": [],
    }
    try:
        result["date"] = find_date(text)
    except ValueError:
        pass  # ocr messed up the date, user can fix it

    m = TOTAL_RE.search(text)
    if m:
        result["total"] = to_num(m.group("total"))

    items = result["items"]
    for line in lines:
        if line.upper().startswith(SKIP_WORDS):
            continue

        m = QTY_RE.match(line)
        if m:
            items.append(
                {
                    "raw_name": m.group("name").strip(),
                    "price": to_num(m.group("unit")),
                    "quantity": to_num(m.group("qty")),
                }
            )
            continue

        m = ITEM_RE.match(line)
        if not m:
            continue
        items.append(
            {
                "raw_name": m.group("name"),
                "price": to_num(m.group("price")),
                "quantity": 1,
            }
        )
    return result
