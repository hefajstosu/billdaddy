import os
import uuid

from flask import Blueprint, current_app, jsonify, request

from ..extensions import db
from ..models import Receipt

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

    receipt = Receipt(image_path=path)
    db.session.add(receipt)
    db.session.commit()

    return jsonify(receipt.to_dict()), 201


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
