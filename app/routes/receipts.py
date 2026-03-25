import os
import uuid
from datetime import date

from flask import Blueprint, current_app, jsonify, request

from ..extensions import db
from ..models import Category, Product, Receipt, ReceiptItem
from ..ocr.parser import parse
from ..ocr.tesseract_engine import read_text
from ..services.categorizer import guess_category
from ..services.normalizer import match_product

bp = Blueprint("receipts", __name__, url_prefix="/api/receipts")

ALLOWED = {"jpg", "jpeg", "png", "webp"}


@bp.route("", methods=["POST"])
def upload():
    f = request.files.get("image")
    if not f or not f.filename:
        return jsonify({"error": "no image"}), 400

    ext = f.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        return jsonify({"error": "bad file type"}), 400

    # every phone names photos IMG_xxxx.jpg so they kept overwriting each other
    filename = "{}.{}".format(uuid.uuid4().hex, ext)
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    f.save(path)

    text = read_text(path)
    print(text)
    parsed = parse(text)

    receipt = Receipt(
        image_path=path,
        shop_name=parsed["shop"],
        purchase_date=parsed["date"],
        total_amount=parsed["total"],
    )
    suggestions = []
    for it in parsed["items"]:
        product, score = match_product(it["raw_name"])
        if product:
            cat = product.category
        else:
            cat = guess_category(it["raw_name"])
        receipt.items.append(ReceiptItem(
            raw_name=it["raw_name"],
            price_per_unit=it["price"],
            quantity=it["quantity"],
            product=product,
        ))
        suggestions.append({
            "score": score,
            "category": cat.to_dict() if cat else None,
        })
    db.session.add(receipt)
    db.session.commit()

    data = receipt.to_dict(with_items=True)
    for item, sug in zip(data["items"], suggestions):
        item.update(sug)
    return jsonify(data), 201


@bp.route("/<int:receipt_id>/confirm", methods=["PUT"])
def confirm(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    data = request.get_json() or {}

    if "shop_name" in data:
        receipt.shop_name = data["shop_name"]
    if data.get("purchase_date"):
        receipt.purchase_date = date.fromisoformat(data["purchase_date"])
    if data.get("total_amount") is not None:
        receipt.total_amount = float(data["total_amount"])

    # just replace all items, frontend sends the whole list anyway
    receipt.items.clear()
    for it in data.get("items", []):
        name = (it.get("product_name") or "").strip()
        if not name:
            return jsonify({"error": "missing product name for " + it.get("raw_name", "?")}), 400

        product = Product.query.filter_by(normalized_name=name).first()
        category_id = it.get("category_id")
        if not product:
            if not category_id or not Category.query.get(category_id):
                return jsonify({"error": "bad category for " + name}), 400
            product = Product(normalized_name=name, category_id=category_id)
            db.session.add(product)
        elif category_id and category_id != product.category_id:
            product.category_id = category_id

        receipt.items.append(ReceiptItem(
            raw_name=it.get("raw_name") or name,
            price_per_unit=float(it["price_per_unit"]),
            quantity=float(it.get("quantity") or 1),
            product=product,
        ))

    receipt.status = "confirmed"
    db.session.commit()

    computed = sum(round(i.price_per_unit * i.quantity, 2) for i in receipt.items)
    result = receipt.to_dict(with_items=True)
    result["computed_total"] = computed
    result["total_mismatch"] = (
        receipt.total_amount is not None and abs(computed - receipt.total_amount) > 0.01
    )
    return jsonify(result)


@bp.route("", methods=["GET"])
def list_receipts():
    receipts = Receipt.query.order_by(Receipt.purchase_date.desc()).all()
    return jsonify([r.to_dict() for r in receipts])


@bp.route("/<int:receipt_id>", methods=["GET"])
def get_receipt(receipt_id):
    r = Receipt.query.get_or_404(receipt_id)
    return jsonify(r.to_dict(with_items=True))


@bp.route("/<int:receipt_id>", methods=["DELETE"])
def delete_receipt(receipt_id):
    r = Receipt.query.get_or_404(receipt_id)
    db.session.delete(r)
    db.session.commit()
    return "", 204
