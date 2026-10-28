"""Module: app.

Purpose: Compose Flask configuration, blueprints, entry pages, error handlers, and CLI commands.
Main components: role-specific login/workspace pages, configuration, security registration, health/errors and database/admin/AI CLI commands.
Related: audia.config, audia.routes, audia.database; root templates/assets and .env.
Debugging: Check startup order here, then the route or service named in the traceback.
"""
import os
import secrets
from datetime import timedelta
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import (
    Flask,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from werkzeug.security import generate_password_hash


# ---------------------------------------------------------
# 1. Load environment variables FIRST
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parent

load_dotenv(ROOT / ".env")


# ---------------------------------------------------------
# 2. Import AUDIA modules AFTER .env has been loaded
# ---------------------------------------------------------

from audia.routes.admin import admin
from audia.routes.auth import (
    auth,
    install_security,
    require_page,
    validate_email,
    validate_password,
)
from audia.routes.catalog import catalog
from audia.routes.chatbot import chatbot
from audia.database import db, init_database, initialize
from audia.database.models import User
from audia.routes.orders import orders
from audia.routes.tuner import tuner
from audia.routes.lessons import lessons, lessons_api


# ---------------------------------------------------------
# 3. Create Flask application
# ---------------------------------------------------------

app = Flask(
    __name__,
    static_folder="assets",
    static_url_path="/static",
    template_folder="templates",
    instance_path=str(ROOT / "instance"),
)


# ---------------------------------------------------------
# 4. Build PostgreSQL database URL
# ---------------------------------------------------------

from audia.config.database import build_database_url


# ---------------------------------------------------------
# 5. Application configuration
# ---------------------------------------------------------

app.config.update(
    DATABASE_URL=build_database_url(),

    SECRET_KEY=os.getenv(
        "SECRET_KEY"
    ),

    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Database LoginSession expiry is fixed; avoid stale concurrent cookie refreshes.
    SESSION_REFRESH_EACH_REQUEST=False,

    SESSION_COOKIE_SECURE=(
        os.getenv(
            "COOKIE_SECURE",
            "false",
        ).lower()
        == "true"
    ),

    PERMANENT_SESSION_LIFETIME=timedelta(
        days=30
    ),

    MAX_CONTENT_LENGTH=64 * 1024,

    MAIL_BACKEND=os.getenv(
        "MAIL_BACKEND",
        "disabled",
    ),

    SMTP_HOST=os.getenv(
        "SMTP_HOST",
        "",
    ),

    SMTP_PORT=int(
        os.getenv(
            "SMTP_PORT",
            "587",
        )
    ),

    SMTP_USER=os.getenv(
        "SMTP_USER",
        "",
    ),

    SMTP_PASSWORD=os.getenv(
        "SMTP_PASSWORD",
        "",
    ),

    SMTP_FROM=os.getenv(
        "SMTP_FROM",
        "noreply@audia.local",
    ),

    APP_URL=os.getenv(
        "APP_URL",
        "http://localhost:5000",
    ).rstrip("/"),
)


# ---------------------------------------------------------
# 6. Secret key fallback
# ---------------------------------------------------------

if not app.config["SECRET_KEY"]:

    Path(
        app.instance_path
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    key_file = (
        Path(app.instance_path)
        / ".secret-key"
    )

    try:
        with key_file.open(
            "x",
            encoding="utf-8",
        ) as file:

            file.write(
                secrets.token_hex(32)
            )

    except FileExistsError:
        pass

    app.config["SECRET_KEY"] = (
        key_file.read_text(
            encoding="utf-8"
        )
    )


# ---------------------------------------------------------
# 7. Initialize PostgreSQL
# ---------------------------------------------------------

init_database(app)


# ---------------------------------------------------------
# 8. Register blueprints
# ---------------------------------------------------------

app.register_blueprint(auth)
app.register_blueprint(catalog)
app.register_blueprint(orders)
app.register_blueprint(admin)

# Gemini chatbot
app.register_blueprint(chatbot)
app.register_blueprint(tuner)
app.register_blueprint(lessons)
app.register_blueprint(lessons_api)


# Install authentication/security hooks
install_security(app)


# ---------------------------------------------------------
# 9. Pages
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template(
        "landing/landing.html",
        title="Find your sound",
        page_name="landing",
        stylesheet="landing/landing",
    )


@app.route("/login")
def login_page():
    # Preserve old administrator bookmarks while keeping a distinct login page.
    if request.args.get('role') == 'admin':
        return redirect(url_for('admin_login_page'))

    if g.user:
        return redirect(
            url_for(
                "dashboard"
                if g.user.role == "admin"
                else "shop"
            )
        )

    return render_template(
        "auth/auth.html",
        title="Sign in",
        page_name="auth",
        stylesheet="auth/auth",
        auth_mode='login',
    )


@app.route('/admin/login')
def admin_login_page():
    """Show the administrator portal; session identity still comes from the database."""
    if g.user:
        return redirect(url_for('dashboard' if g.user.role == 'admin' else 'shop'))
    return render_template('auth/auth.html', title='Administrator sign in', page_name='auth',
                           stylesheet='auth/auth', auth_mode='admin')


@app.route("/register")
def register_page():

    if g.user:
        return redirect(
            url_for('dashboard' if g.user.role == 'admin' else 'shop')
        )

    return render_template(
        "auth/auth.html",
        title="Create an account",
        page_name="auth",
        stylesheet="auth/auth",
        auth_mode="register",
    )


@app.route("/reset-password")
def reset_password_page():

    return render_template(
        "auth/auth.html",
        title="Reset your password",
        page_name="auth",
        stylesheet="auth/auth",
        auth_mode="reset",
        reset_token=request.args.get(
            "token",
            "",
        ),
    )


@app.route("/shop")
@require_page(role='customer')
def shop():
    """Customer storefront; the reusable page guard rejects other roles."""
    return render_template(
        "catalog/catalog.html",
        title="Guitar shop",
        page_name="storefront",
        stylesheet="catalog/catalog",
    )


@app.route("/account")
@require_page()
def account_page():
    """Shared profile/password page with role-specific navigation and sections."""
    return render_template(
        "account/account.html",
        title="My account",
        page_name="account",
        stylesheet="account/account",
    )


@app.route("/orders")
@require_page(role='customer')
def orders_page():
    """Render the authenticated order/tracking workspace with existing account styles."""
    return render_template("account/orders.html", title="My Orders", page_name="orders", stylesheet="account/account")


@app.route("/admin")
@require_page(role='admin')
def dashboard():
    """Administrator workspace; customers receive a 403 before rendering."""
    return render_template(
        "admin/admin.html",
        title="Administration",
        page_name="dashboard",
        stylesheet="admin/admin",
    )


# ---------------------------------------------------------
# 10. Health endpoint
# ---------------------------------------------------------

@app.route("/api/health")
def health():

    """Return database readiness JSON for the configured application.

    Executes SELECT 1 when configured; SQL connectivity errors reach
    database_unavailable(), while missing configuration returns 503.
    """
    if "engine" not in current_app.extensions:

        return jsonify(
            status="setup_required",
            database="not_configured",
        ), 503

    db().execute(
        text("SELECT 1")
    )

    return jsonify(
        status="ok",
        service="AUDIA",
        database="connected",
    )

# ---------------------------------------------------------
# 11. Error handlers
# ---------------------------------------------------------

@app.errorhandler(
    OperationalError
)
def database_unavailable(error):

    if g.get("db"):
        g.db.rollback()

    return jsonify(
        error=(
            "The database is unavailable. "
            "Please try again shortly."
        )
    ), 503


@app.errorhandler(503)
def service_unavailable(error):

    return jsonify(
        error=(
            "Account and order services "
            "are not available yet. "
            "Please try again later."
        )
    ), 503


@app.errorhandler(413)
def request_too_large(error):

    return jsonify(
        error="This request is too large."
    ), 413


# ---------------------------------------------------------
# 12. CLI: initialize database
# ---------------------------------------------------------

@app.cli.command(
    "init-db"
)
def init_db():
    """
    Create missing tables and seed an empty
    catalog without deleting existing data.
    """

    initialize(
        current_app
    )

    click.echo(
        "Database ready. "
        "Catalog seed applied where needed."
    )


@app.cli.command("upgrade-db")
def upgrade_db():
    """Back up records, add missing feature tables and enforce the single-admin index."""
    from audia.database.migrations import upgrade_database
    try:
        backup = upgrade_database(current_app)
        click.echo(f"Database upgraded. Private backup: {backup}" if backup else "Database is already up to date.")
    except Exception as error:
        current_app.logger.exception("Additive database upgrade failed.")
        raise click.ClickException("Database upgrade failed. Check the server log; existing tables are unchanged.") from error


# ---------------------------------------------------------
# 13. CLI: create administrator
# ---------------------------------------------------------

@app.cli.command(
    "create-admin"
)
@click.option(
    "--email",
    prompt=True,
)
@click.option(
    "--name",
    default="AUDIA Admin",
    prompt=True,
)
@click.password_option()
def create_admin(
    email,
    name,
    password,
):

    """Create an administrator from prompted email, name, and password.

    Uses auth validators and database.User; invalid or existing email input
    raises ClickException. Database errors propagate without changing logic.
    """
    try:

        email = validate_email(
            email
        )

        validate_password(
            password
        )

    except ValueError as error:

        raise click.ClickException(
            str(error)
        ) from error

    existing_user = (
        db()
        .query(User)
        .filter_by(
            email=email
        )
        .first()
    )

    if existing_user:

        raise click.ClickException(
            "That email already exists; "
            "no account was changed."
        )

    if db().scalar(select(User.id).where(User.role == 'admin').limit(1)) is not None:
        raise click.ClickException('An administrator already exists. No account was changed.')

    admin_user = User(
        name=name.strip(),
        email=email,
        password_hash=generate_password_hash(
            password
        ),
        role="admin",
    )

    db().add(
        admin_user
    )

    try:
        db().commit()
    except IntegrityError as error:
        db().rollback()
        raise click.ClickException('Administrator creation was blocked. Check the existing administrator and email.') from error

    click.echo(
        "Administrator created."
    )

@app.cli.command("sync-rag")
def sync_rag():
    """
    Synchronize AUDIA product knowledge
    with the RAG database.
    """

    from audia.services.ai.ai_rag_sync import (
        sync_products_to_rag,
    )

    try:

        result = sync_products_to_rag()

        click.echo(
            f"RAG synchronization complete. "
            f"{result['indexed']} products indexed, "
            f"{result['removed']} stale documents removed."
        )

    except Exception:

        db().rollback()

        current_app.logger.exception(
            "RAG synchronization failed."
        )

        raise click.ClickException(
            "RAG synchronization failed. "
            "Check the error above."
        )
# ---------------------------------------------------------
# 14. Run development server
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",

        port=int(
            os.getenv(
                "PORT",
                "5000",
            )
        ),

        debug=(
            os.getenv(
                "FLASK_DEBUG",
                "0",
            )
            == "1"
        ),
    )
