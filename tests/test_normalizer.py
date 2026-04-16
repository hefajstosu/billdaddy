from app.services.categorizer import guess_category_name
from app.services.normalizer import clean, match_product


def test_clean():
    assert clean("ML.ŁACIATE 3,2% 1L") == "mleko laciate 3.2%"
    assert clean("CHLEB ŻYTNI 500G") == "chleb zytni"


def test_match(app):
    p, score = match_product("ML.ŁACIATE 3,2% 1L")
    assert p.normalized_name == "Mleko 3.2%"
    p, _ = match_product("CZEK.MILKA ALPEJSKA")
    assert p.normalized_name == "Czekolada Milka"


def test_no_false_matches(app):
    for raw in ["CHIPSY LAYS 140G", "CHUSTECZKI", "COCA COLA 1,5L"]:
        p, _ = match_product(raw)
        assert p is None, raw


def test_categorizer():
    assert guess_category_name("CZEK.GORZKA") == "Słodycze"
    assert guess_category_name("DOMESTOS 1L") == "Chemia gospodarcza"
    assert guess_category_name("COS DZIWNEGO") == "Inne"
