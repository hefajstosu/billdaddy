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

    from .routes import receipts
    app.register_blueprint(receipts.bp)

    @app.route("/")
    def index():
        return "billdaddy"

    return app
