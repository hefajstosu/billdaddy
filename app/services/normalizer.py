from thefuzz import process

from ..models import Product

THRESHOLD = 50


def match_product(raw_name):
    products = Product.query.all()
    if not products:
        return None, 0

    choices = {p.id: p.normalized_name for p in products}
    name, score, pid = process.extractOne(raw_name, choices)
    print(raw_name, "->", name, score)
    if score < THRESHOLD:
        return None, score
    return Product.query.get(pid), score
