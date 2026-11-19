import os

# set before importing app so Config doesn't warn about the dev fallback
os.environ.setdefault("SECRET_KEY", "test")

import pytest

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import Category, Product, User


# setting the uri after create_app does nothing, db is already bound -> tests hit mysql
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    OCR_ENGINE = "tesseract"
    FUZZY_THRESHOLD = 80


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        for name in ["Nabiał", "Pieczywo", "Słodycze", "Napoje", "Chemia gospodarcza", "Inne"]:
            db.session.add(Category(name=name))
        db.session.commit()
        cat = {c.name: c.id for c in Category.query.all()}
        for name, c in [
            ("Mleko 3.2%", "Nabiał"),
            ("Chleb", "Pieczywo"),
            ("Czekolada Milka", "Słodycze"),
            ("Papier toaletowy", "Chemia gospodarcza"),
        ]:
            db.session.add(Product(normalized_name=name, category_id=cat[c]))
        user = User(username="test")
        user.set_password("test")
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    c = app.test_client()
    c.post("/login", data={"username": "test", "password": "test"})
    return c
