import pytest

from app import create_app
from app.extensions import db
from app.models import Category, Product


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with app.app_context():
        db.create_all()
        for name in ["Nabiał", "Pieczywo", "Słodycze", "Napoje", "Chemia gospodarcza", "Inne"]:
            db.session.add(Category(name=name))
        db.session.commit()
        cat = {c.name: c.id for c in Category.query.all()}
        for name, c in [("Mleko 3.2%", "Nabiał"), ("Chleb", "Pieczywo"),
                        ("Czekolada Milka", "Słodycze"), ("Papier toaletowy", "Chemia gospodarcza")]:
            db.session.add(Product(normalized_name=name, category_id=cat[c]))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
