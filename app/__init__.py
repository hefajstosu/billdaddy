from flask import Flask

from .config import Config
from .extensions import db, migrate


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa

    from .routes import auth, main, receipts, stats
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(receipts.bp)
    app.register_blueprint(stats.bp)

    return app
