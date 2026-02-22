from flask import Flask

from .config import Config
from .extensions import db


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    from . import models  # noqa

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return "billdaddy"

    return app
