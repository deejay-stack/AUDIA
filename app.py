"""AUDIA application factory and root entry point."""

import os
import secrets
from datetime import timedelta
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from sqlalchemy import URL
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash

from modules.database import init_database, db
from modules.models import User


# ---------------------------------------------------------
# Project root and environment variables
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parent

# Load environment variables from:
# audia/.env
load_dotenv(ROOT / ".env")


# ---------------------------------------------------------
# Database URL
# ---------------------------------------------------------

def build_database_url():
    """
    Build the PostgreSQL database URL using credentials
    stored separately inside the .env file.

    Returns an empty string if the required database
    configuration has not been provided yet.
    """

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")

    # If required credentials are missing,
    # treat the database as not configured.
    if not db_user or not db_password or not db_name:
        return os.getenv("DATABASE_URL", "")

    return URL.create(
        drivername="postgresql+psycopg",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name,
    )


# ---------------------------------------------------------
# Flask application factory
# ---------------------------------------------------------

def create_app(config=None):

    application = Flask(
        __name__,
        static_folder="assets",
        static_url_path="/static",
        template_folder="templates",
        instance_path=str(ROOT / "instance"),
    )

    # -----------------------------------------------------
    # Application configuration
    # -----------------------------------------------------

    application.config.update(

        # PostgreSQL
        DATABASE_URL=build_database_url(),

        # Flask security
        SECRET_KEY=os.getenv("SECRET_KEY"),

        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",

        SESSION_COOKIE_SECURE=(
            os.getenv("COOKIE_SECURE", "false").lower() == "true"
        ),

        PERMANENT_SESSION_LIFETIME=timedelta(days=30),

        # Maximum request/upload size
        MAX_CONTENT_LENGTH=64 * 1024,

        # Email configuration
        MAIL_BACKEND=os.getenv("MAIL_BACKEND", "disabled"),

        SMTP_HOST=os.getenv("SMTP_HOST", ""),

        SMTP_PORT=int(
            os.getenv("SMTP_PORT", "587")
        ),

        SMTP_USER=os.getenv("SMTP_USER", ""),

        SMTP_PASSWORD=os.getenv("SMTP_PASSWORD", ""),

        SMTP_FROM=os.getenv(
            "SMTP_FROM",
            "noreply@audia.local"
        ),

        # Application URL
        APP_URL=os.getenv(
            "APP_URL",
            "http://localhost:5000"
        ).rstrip("/"),
    )

    # Allows tests or other environments to override config
    if config:
        application.config.update(config)

    # -----------------------------------------------------
    # Secret key fallback
    # -----------------------------------------------------

    if not application.config["SECRET_KEY"]:

        Path(application.instance_path).mkdir(
            parents=True,
            exist_ok=True
        )

        key_path = (
            Path(application.instance_path)
            / ".secret-key"
        )

        try:
            with key_path.open(
                "x",
                encoding="utf-8"
            ) as key_file:

                key_file.write(
                    secrets.token_hex(32)
                )

        except FileExistsError:
            pass

        application.config["SECRET_KEY"] = (
            key_path.read_text(
                encoding="utf-8"
            )
        )

    # -----------------------------------------------------
    # Database initialization
    # -----------------------------------------------------

    init_database(application)

    # -----------------------------------------------------
    # Blueprints
    # -----------------------------------------------------

    from modules.auth import auth, install_security
    from modules.catalog import catalog
    from modules.orders import orders
    from modules.admin import admin

    for blueprint in (
        auth,
        catalog,
        orders,
        admin,
    ):
        application.register_blueprint(
            blueprint
        )

    install_security(application)

    # -----------------------------------------------------
    # Home page
    # -----------------------------------------------------

    @application.get("/")
    def index():
        return render_template(
            "layouts/index.html"
        )

    # -----------------------------------------------------
    # Database health check
    # -----------------------------------------------------

    @application.get("/api/health")
    def health():

        if "engine" not in application.extensions:

            return jsonify(
                status="setup_required",
                database="not_configured"
            ), 503

        from sqlalchemy import text

        db().execute(
            text("SELECT 1")
        )

        return jsonify(
            status="ok",
            service="AUDIA",
            database="connected"
        )

    # -----------------------------------------------------
    # Error handlers
    # -----------------------------------------------------

    @application.errorhandler(
        OperationalError
    )
    def unavailable(error):

        db().rollback()

        return jsonify(
            error=(
                "The database is unavailable. "
                "Please try again shortly."
            )
        ), 503

    @application.errorhandler(503)
    def not_configured(error):

        return jsonify(
            error=(
                "Account and order services "
                "are not available yet. "
                "Please try again later."
            )
        ), 503

    @application.errorhandler(413)
    def too_large(error):

        return jsonify(
            error="This request is too large."
        ), 413

    # -----------------------------------------------------
    # CLI command: initialize database
    # -----------------------------------------------------

    @application.cli.command(
        "init-db"
    )
    def init_db():
        """
        Create missing tables and seed the catalog
        without erasing existing data.
        """

        from modules.database import initialize

        initialize(application)

        click.echo(
            "Database ready. "
            "Catalog seed applied where needed."
        )

    # -----------------------------------------------------
    # CLI command: create administrator
    # -----------------------------------------------------

    @application.cli.command(
        "create-admin"
    )
    @click.option(
        "--email",
        prompt=True
    )
    @click.option(
        "--name",
        default="AUDIA Admin",
        prompt=True
    )
    @click.password_option()
    def create_admin(
        email,
        name,
        password
    ):
        """
        Create an administrator explicitly,
        with no default password.
        """

        from modules.auth import (
            validate_email,
            validate_password,
        )

        try:

            email = validate_email(email)

            validate_password(password)

        except ValueError as error:

            raise click.ClickException(
                str(error)
            ) from error

        existing_user = (
            db()
            .query(User)
            .filter_by(email=email)
            .first()
        )

        if existing_user:

            raise click.ClickException(
                "That email already exists; "
                "no account was changed."
            )

        admin_user = User(
            name=name.strip(),
            email=email,
            password_hash=generate_password_hash(
                password
            ),
            role="admin",
        )

        db().add(admin_user)

        db().commit()

        click.echo(
            "Administrator created."
        )

    return application


# ---------------------------------------------------------
# Create Flask application
# ---------------------------------------------------------

app = create_app()


# ---------------------------------------------------------
# Development server
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=int(
            os.getenv(
                "PORT",
                "5000"
            )
        ),
        debug=(
            os.getenv(
                "FLASK_DEBUG",
                "0"
            ) == "1"
        ),
    )
