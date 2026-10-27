import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

database = SQLAlchemy()

# Insecure fallback used only when SECRET_KEY is not provided. Never rely on
# this in production: sessions signed with it can be forged by anyone.
DEV_SECRET_KEY = "dev-only-insecure-secret-key"

# Flask-SQLAlchemy option applied to SQLite so that concurrent gunicorn
# workers wait for the write lock instead of failing with "database is locked".
SQLITE_TIMEOUT_SECONDS = 30


def create_app(config=None):
    """Application factory.

    Configuration precedence: explicit ``config`` mapping, then environment
    variables, then defaults (SQLite under the Flask instance folder).
    """
    app = Flask(__name__, instance_relative_config=True)

    if config:
        app.config.from_mapping(config)

    app.config["SECRET_KEY"] = _secret_key(app)
    instance_path = _ensure_instance_path(app)

    database_url = (
        app.config.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("DATABASE_URL")
    )
    if not database_url:
        database_url = "sqlite:///{}".format(instance_path / "postagram.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    if database_url.startswith("sqlite:") and "SQLALCHEMY_ENGINE_OPTIONS" not in app.config:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"timeout": SQLITE_TIMEOUT_SECONDS}
        }

    database.init_app(app)

    from .home import home
    app.register_blueprint(home, url_prefix="/")

    from .auth import auth
    app.register_blueprint(auth, url_prefix="/")

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import Users

    @login_manager.user_loader
    def load_user(username):
        return Users.query.get(username)

    return app


def _secret_key(app):
    secret_key = app.config.get("SECRET_KEY") or os.environ.get("SECRET_KEY")
    if secret_key:
        return secret_key
    app.logger.warning(
        "SECRET_KEY is not set. Using an insecure development fallback; "
        "set SECRET_KEY before deploying to production."
    )
    return DEV_SECRET_KEY


def _ensure_instance_path(app):
    """Create the instance folder and fail early if it is not writable."""
    instance_path = Path(app.instance_path)
    try:
        instance_path.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise RuntimeError(
            f"Could not create instance directory '{instance_path}': {error}"
        ) from error
    if not os.access(instance_path, os.W_OK | os.X_OK):
        raise RuntimeError(
            f"Instance directory '{instance_path}' is not writable."
        )
    return instance_path


def create_database(app):
    """Create any missing tables for the configured database (idempotent).

    This replaces the previous MySQL-only "show databases / create database"
    bootstrap. For MySQL/MariaDB the database itself must already exist.
    """
    with app.app_context():
        database.create_all()
