from datetime import datetime

from .extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship("Product", backref="category")

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    normalized_name = db.Column(db.String(200), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.normalized_name,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
        }


class Receipt(db.Model):
    __tablename__ = "receipts"

    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    total_amount = db.Column(db.Float)
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default="draft", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "ReceiptItem", backref="receipt", cascade="all, delete-orphan"
    )

    def to_dict(self, with_items=False):
        d = {
            "id": self.id,
            "shop_name": self.shop_name,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "total_amount": self.total_amount,
            "status": self.status,
        }
        if with_items:
            d["items"] = [i.to_dict() for i in self.items]
        return d


class ReceiptItem(db.Model):
    __tablename__ = "receipt_items"

    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey("receipts.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    raw_name = db.Column(db.String(200), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, default=1)

    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "raw_name": self.raw_name,
            "price_per_unit": self.price_per_unit,
            "quantity": self.quantity,
            "product": self.product.to_dict() if self.product else None,
        }
