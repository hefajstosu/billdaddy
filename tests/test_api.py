from datetime import date
from decimal import Decimal
from io import BytesIO

import pytest

from app.models import Product


def fake_extract(items, d=date(2026, 11, 2), total="10.00"):
    def _extract(path):
        return {"shop": "Biedronka", "date": d, "total": Decimal(total), "items": items}
    return _extract


@pytest.fixture
def upload(client, monkeypatch, tmp_path):
    def _upload(items, **kw):
        client.application.config["UPLOAD_FOLDER"] = str(tmp_path)
        monkeypatch.setattr("app.routes.receipts.extract", fake_extract(items, **kw))
        res = client.post("/api/receipts", data={"image": (BytesIO(b"x"), "p.jpg")})
        assert res.status_code == 201
        return res.get_json()
    return _upload


def item(name, price, qty="1"):
    return {"raw_name": name, "price": Decimal(price), "quantity": Decimal(qty)}


def test_upload_requires_image(client):
    assert client.post("/api/receipts").status_code == 400


def test_upload_bad_extension(client):
    res = client.post("/api/receipts", data={"image": (BytesIO(b"x"), "p.exe")})
    assert res.status_code == 400


def test_upload_ocr_error(client, monkeypatch, tmp_path):
    from app.ocr import OcrError

    client.application.config["UPLOAD_FOLDER"] = str(tmp_path)

    def boom(path):
        raise OcrError("could not read receipt: bad photo")

    monkeypatch.setattr("app.routes.receipts.extract", boom)
    res = client.post("/api/receipts", data={"image": (BytesIO(b"x"), "p.jpg")})
    assert res.status_code == 422
    assert "bad photo" in res.get_json()["error"]


def test_upload_suggestions(upload):
    r = upload([item("ML.ŁACIATE 3,2% 1L", "3.49", "2"), item("COCA COLA 1,5L", "7.49")])
    assert r["status"] == "draft"
    assert r["items"][0]["product"]["name"] == "Mleko 3.2%"
    assert r["items"][1]["product"] is None
    assert r["items"][1]["category"]["name"] == "Napoje"


def confirm_body(r, names, cat_id=None):
    return {
        "shop_name": r["shop_name"],
        "purchase_date": r["purchase_date"],
        "total_amount": r["total_amount"],
        "items": [
            {"raw_name": i["raw_name"], "product_name": n, "category_id": cat_id,
             "price_per_unit": i["price_per_unit"], "quantity": i["quantity"]}
            for i, n in zip(r["items"], names)
        ],
    }


def test_confirm_creates_product(client, upload):
    r = upload([item("COCA COLA 1,5L", "7.49")], total="7.49")
    napoje = next(c for c in client.get("/api/categories").get_json() if c["name"] == "Napoje")
    res = client.put(f"/api/receipts/{r['id']}/confirm", json=confirm_body(r, ["Coca-Cola 1.5L"], napoje["id"]))
    data = res.get_json()
    assert res.status_code == 200
    assert data["status"] == "confirmed"
    assert data["total_mismatch"] is False
    assert Product.query.filter_by(normalized_name="Coca-Cola 1.5L").first().category.name == "Napoje"

    # next time same raw name is matched straight away
    r2 = upload([item("COCA COLA 1,5L", "7.99")])
    assert r2["items"][0]["product"]["name"] == "Coca-Cola 1.5L"


def test_confirm_new_product_needs_category(client, upload):
    r = upload([item("COS", "1.00")])
    res = client.put(f"/api/receipts/{r['id']}/confirm", json=confirm_body(r, ["Coś"]))
    assert res.status_code == 400


def test_rounding_half_up(client, upload):
    # 0.5 x 5.35 = 2.675 -> receipt says 2.68
    r = upload([item("CHLEB", "5.35", "0.5")], total="2.68")
    res = client.put(f"/api/receipts/{r['id']}/confirm", json=confirm_body(r, ["Chleb"]))
    assert res.get_json()["computed_total"] == 2.68
    assert res.get_json()["total_mismatch"] is False


def test_stats_and_price_history(client, upload):
    for d, price in [(date(2026, 10, 1), "3.49"), (date(2026, 11, 1), "3.79")]:
        r = upload([item("ML.ŁACIATE 3,2% 1L", price, "2")], d=d)
        client.put(f"/api/receipts/{r['id']}/confirm", json=confirm_body(r, ["Mleko 3.2%"]))

    stats = client.get("/api/stats/categories").get_json()
    assert stats == [{"category": "Nabiał", "total": 14.56}]
    assert client.get("/api/stats/categories?from=2026-11-01").get_json()[0]["total"] == 7.58

    mleko = Product.query.filter_by(normalized_name="Mleko 3.2%").first()
    hist = client.get(f"/api/stats/prices/{mleko.id}").get_json()
    assert [p["price"] for p in hist["points"]] == [3.49, 3.79]
    assert hist["change_pct"] == 8.6


def test_drafts_not_in_stats(client, upload):
    upload([item("ML.ŁACIATE 3,2% 1L", "3.49")])
    assert client.get("/api/stats/categories").get_json() == []


def test_delete(client, upload):
    r = upload([item("CHLEB", "4.29")])
    assert client.delete(f"/api/receipts/{r['id']}").status_code == 204
    assert client.get(f"/api/receipts/{r['id']}").status_code == 404
