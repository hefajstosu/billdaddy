from flask import Blueprint, jsonify, render_template

from ..auth import login_required
from ..models import Category, Product

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def index():
    return render_template("index.html")


@bp.route("/api/categories")
@login_required
def categories():
    return jsonify([c.to_dict() for c in Category.query.order_by(Category.name).all()])


@bp.route("/api/products")
@login_required
def products():
    return jsonify([p.to_dict() for p in Product.query.order_by(Product.normalized_name).all()])
