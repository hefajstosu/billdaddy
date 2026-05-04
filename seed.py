import os

from app import create_app
from app.extensions import db
from app.models import Category, Product, User

CATEGORIES = [
    "Warzywa i owoce",
    "Nabiał",
    "Pieczywo",
    "Mięso i wędliny",
    "Słodycze",
    "Napoje",
    "Alkohol",
    "Chemia gospodarcza",
    "Higiena",
    "Zachcianki",
    "Inne",
]

PRODUCTS = {
    "Mleko 3.2%": "Nabiał",
    "Masło 82%": "Nabiał",
    "Jogurt naturalny": "Nabiał",
    "Chleb": "Pieczywo",
    "Bułka kajzerka": "Pieczywo",
    "Czekolada Milka": "Słodycze",
    "Papier toaletowy": "Chemia gospodarcza",
    "Banany": "Warzywa i owoce",
    "Pomidory": "Warzywa i owoce",
    "Woda mineralna": "Napoje",
}

app = create_app()

with app.app_context():
    # can be run multiple times
    for name in CATEGORIES:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    db.session.commit()

    for name, cat in PRODUCTS.items():
        if Product.query.filter_by(normalized_name=name).first():
            continue
        c = Category.query.filter_by(name=cat).first()
        db.session.add(Product(normalized_name=name, category_id=c.id))

    username = os.getenv("ADMIN_USERNAME", "admin")
    if not User.query.filter_by(username=username).first():
        user = User(username=username)
        user.set_password(os.getenv("ADMIN_PASSWORD", "admin"))
        db.session.add(user)

    db.session.commit()
    print("ok")
