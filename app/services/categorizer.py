from ..models import Category

DEFAULT = "Inne"

# keyword -> category, checked against upper case raw name
# TODO: move this to db so user can edit it
KEYWORDS = {
    "Nabiał": ["MLEKO", "ML.", "MLECZ", "SER ", "SEREK", "JOGURT", "JOG.", "MASŁO", "MASLO",
               "ŚMIETANA", "SMIETANA", "KEFIR", "TWARÓG", "TWAROG", "JAJA"],
    "Pieczywo": ["CHLEB", "BUŁKA", "BULKA", "BAGIETKA", "ROGAL", "KAJZERKA"],
    "Mięso i wędliny": ["SZYNKA", "KIEŁBASA", "KIELBASA", "FILET", "KURCZAK", "PARÓWKI",
                        "PAROWKI", "BOCZEK", "SCHAB", "MIĘSO", "MIESO", "SALAMI"],
    "Warzywa i owoce": ["BANAN", "JABŁ", "JABL", "POMIDOR", "OGÓR", "OGOR", "ZIEMNIAK",
                        "CEBULA", "MARCHEW", "PAPRYKA", "CYTRYN", "POMARAŃCZ", "POMARANCZ",
                        "SAŁATA", "SALATA", "LUZ"],
    "Słodycze": ["CZEK", "BATON", "WAFL", "CUKIERK", "ŻELKI", "ZELKI", "MILKA", "WEDEL",
                 "LODY", "CIASTK", "DONUT", "PRINCESSA"],
    "Zachcianki": ["CHIPS", "LAYS", "PRINGLES", "ORZESZKI", "PIZZA", "PALUSZKI"],
    "Napoje": ["WODA", "SOK", "COLA", "PEPSI", "NAPÓJ", "NAPOJ", "HERBATA", "KAWA", "FANTA"],
    "Alkohol": ["PIWO", "WINO", "WÓDKA", "WODKA", "WHISKY", "TYSKIE", "ŻYWIEC PIWO"],
    "Chemia gospodarcza": ["PAPIER", "RĘCZNIK", "RECZNIK", "DOMESTOS", "PŁYN", "PLYN",
                           "PROSZEK", "KAPSUŁKI", "KAPSULKI", "WORKI", "GĄBKI", "GABKI",
                           "FAIRY", "LENOR", "VANISH"],
    "Higiena": ["SZAMPON", "PASTA DO ZĘB", "PASTA DO ZEB", "MYDŁO", "MYDLO", "DEZODORANT",
                "ŻEL POD", "ZEL POD", "CHUSTECZKI", "PODPASKI", "MASZYNKA"],
}


def guess_category_name(raw_name):
    name = raw_name.upper()
    for cat, words in KEYWORDS.items():
        for w in words:
            if w in name:
                return cat
    return DEFAULT


def guess_category(raw_name):
    return Category.query.filter_by(name=guess_category_name(raw_name)).first()
