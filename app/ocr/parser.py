import re

# NAME  qty x unit_price  total + PTU letter
# ocr sometimes adds garbage like "(1" or "S5,13C" so regex is a bit loose
QTY_RE = re.compile(
    r"^(?P<name>.+?)\s+\(?(?P<qty>\d+(?:[.,]\d+)?)[A-Za-z]?\s*[xX*]\s*"
    r"(?P<unit>\d+[.,]\d{2})\s+\S*?(?P<total>\d+[.,]\d{2})\S*$"
)
# NAME ...  price + PTU letter at the end
ITEM_RE = re.compile(r"^(?P<name>.+?)\s+(?P<price>\d+[.,]\d{2})\s*[A-G]?$")


def to_num(s):
    return float(s.replace(",", ".").replace(" ", ""))


def parse(text):
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = QTY_RE.match(line)
        if m:
            items.append({
                "raw_name": m.group("name").strip(),
                "price": to_num(m.group("unit")),
                "quantity": to_num(m.group("qty")),
            })
            continue

        m = ITEM_RE.match(line)
        if not m:
            continue
        items.append({
            "raw_name": m.group("name"),
            "price": to_num(m.group("price")),
            "quantity": 1,
        })
    return {"items": items}
