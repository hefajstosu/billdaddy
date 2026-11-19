from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from ..auth import login_required
from ..extensions import db
from ..models import Category, Product, Receipt, ReceiptItem

bp = Blueprint("stats", __name__, url_prefix="/api/stats")


def _date_arg(name):
    v = request.args.get(name)
    return date.fromisoformat(v) if v else None


@bp.route("/categories")
@login_required
def by_category():
    total = func.sum(ReceiptItem.price_per_unit * ReceiptItem.quantity)
    q = (
        db.session.query(Category.name, total)
        .join(Product, Product.category_id == Category.id)
        .join(ReceiptItem, ReceiptItem.product_id == Product.id)
        .join(Receipt, Receipt.id == ReceiptItem.receipt_id)
        .filter(Receipt.status == "confirmed")
    )
    d_from, d_to = _date_arg("from"), _date_arg("to")
    if d_from:
        q = q.filter(Receipt.purchase_date >= d_from)
    if d_to:
        q = q.filter(Receipt.purchase_date <= d_to)

    rows = q.group_by(Category.name).order_by(total.desc()).all()
    return jsonify([{"category": name, "total": round(float(t), 2)} for name, t in rows])


@bp.route("/prices/<int:product_id>")
@login_required
def price_history(product_id):
    product = db.get_or_404(Product, product_id)
    rows = (
        db.session.query(Receipt.purchase_date, Receipt.shop_name, ReceiptItem.price_per_unit)
        .join(ReceiptItem, ReceiptItem.receipt_id == Receipt.id)
        .filter(ReceiptItem.product_id == product_id)
        .filter(Receipt.status == "confirmed")
        .filter(Receipt.purchase_date.isnot(None))
        .order_by(Receipt.purchase_date)
        .all()
    )
    points = [{"date": d.isoformat(), "shop": shop, "price": float(p)} for d, shop, p in rows]

    change = None
    if len(points) >= 2 and points[0]["price"]:
        change = round((points[-1]["price"] - points[0]["price"]) / points[0]["price"] * 100, 1)

    return jsonify({"product": product.to_dict(), "points": points, "change_pct": change})
