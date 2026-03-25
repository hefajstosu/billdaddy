import re

from flask import current_app
from thefuzz import fuzz, process

from ..models import Product

PL = str.maketrans("ąćęłńóśźż", "acelnoszz")

# shop abbreviations -> full words
ABBR = {
    "ml.": "mleko ",
    "czek.": "czekolada ",
    "jog.": "jogurt ",
    "toal.": "toaletowy ",
    "pap.": "papier ",
    "ser.": "serek ",
    "szt.": "",
}

# 500g, 1l, 1,5l, 8r, 400ml ...
SIZE_RE = re.compile(r"\b\d+([.,]\d+)?\s?(g|kg|l|ml|r|szt)\b")


def clean(name):
    s = name.lower().translate(PL)
    for k, v in ABBR.items():
        s = s.replace(k, v)
    s = SIZE_RE.sub(" ", s)
    s = s.replace(",", ".")
    s = re.sub(r"[^a-z0-9.% ]", " ", s)
    return " ".join(s.split())


def match_product(raw_name):
    products = Product.query.all()
    if not products:
        return None, 0

    choices = {p.id: clean(p.normalized_name) for p in products}
    name, score, pid = process.extractOne(
        clean(raw_name), choices, scorer=fuzz.token_set_ratio, processor=None
    )
    if score < current_app.config["FUZZY_THRESHOLD"]:
        return None, score
    return Product.query.get(pid), score
