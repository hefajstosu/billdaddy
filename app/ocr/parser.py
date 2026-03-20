import re

# NAME ...  price + PTU letter at the end
ITEM_RE = re.compile(r"^(?P<name>.+?)\s+(?P<price>\d+[.,]\d{2})\s*[A-G]?$")


def parse(text):
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = ITEM_RE.match(line)
        if not m:
            continue
        items.append({
            "raw_name": m.group("name"),
            "price": float(m.group("price")),
            "quantity": 1,
        })
    return {"items": items}
