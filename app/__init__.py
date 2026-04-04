from flask import Flask

from .config import Config
from .extensions import db, migrate


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa

    from .routes import receipts
    app.register_blueprint(receipts.bp)

    @app.route("/")
    def index():
        return "billdaddy"

    return app
