from app import create_app
from app.extensions import db
from app.models import Category, Product

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
    for name in CATEGORIES:
        db.session.add(Category(name=name))
    db.session.commit()

    for name, cat in PRODUCTS.items():
        c = Category.query.filter_by(name=cat).first()
        db.session.add(Product(normalized_name=name, category_id=c.id))
    db.session.commit()
    print("ok")
