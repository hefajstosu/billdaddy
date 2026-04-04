from flask import Blueprint, jsonify

from ..models import Category, Product

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return "billdaddy"


@bp.route("/api/categories")
def categories():
    return jsonify([c.to_dict() for c in Category.query.order_by(Category.name).all()])


@bp.route("/api/products")
def products():
    return jsonify([p.to_dict() for p in Product.query.order_by(Product.normalized_name).all()])
