"""AUDIA application factory and root entry point."""
import os
import secrets
from datetime import timedelta
from pathlib import Path
import click
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash
from modules.database import init_database, db
from modules.models import User

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')


def create_app(config=None):
    application = Flask(__name__, static_folder='assets', static_url_path='/static',
                        template_folder='templates', instance_path=str(ROOT / 'instance'))
    application.config.update(
        DATABASE_URL=os.getenv('DATABASE_URL', ''), SECRET_KEY=os.getenv('SECRET_KEY'),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
        PERMANENT_SESSION_LIFETIME=timedelta(days=30), MAX_CONTENT_LENGTH=64 * 1024,
        MAIL_BACKEND=os.getenv('MAIL_BACKEND', 'disabled'),
        SMTP_HOST=os.getenv('SMTP_HOST', ''), SMTP_PORT=int(os.getenv('SMTP_PORT', '587')),
        SMTP_USER=os.getenv('SMTP_USER', ''), SMTP_PASSWORD=os.getenv('SMTP_PASSWORD', ''),
        SMTP_FROM=os.getenv('SMTP_FROM', 'noreply@audia.local'),
        APP_URL=os.getenv('APP_URL', 'http://localhost:5000').rstrip('/'),
    )
    if config:
        application.config.update(config)
    if not application.config['SECRET_KEY']:
        Path(application.instance_path).mkdir(parents=True, exist_ok=True)
        key_path = Path(application.instance_path) / '.secret-key'
        try:
            with key_path.open('x', encoding='utf-8') as key_file:
                key_file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        application.config['SECRET_KEY'] = key_path.read_text(encoding='utf-8')
    init_database(application)
    from modules.auth import auth, install_security
    from modules.catalog import catalog
    from modules.orders import orders
    from modules.admin import admin
    for blueprint in (auth, catalog, orders, admin):
        application.register_blueprint(blueprint)
    install_security(application)

    @application.get('/')
    def index():
        return render_template('layouts/index.html')

    @application.get('/api/health')
    def health():
        if 'engine' not in application.extensions:
            return jsonify(status='setup_required', database='not_configured'), 503
        from sqlalchemy import text
        db().execute(text('SELECT 1'))
        return jsonify(status='ok', service='AUDIA', database='connected')

    @application.errorhandler(OperationalError)
    def unavailable(error):
        db().rollback()
        return jsonify(error='The database is unavailable. Please try again shortly.'), 503

    @application.errorhandler(503)
    def not_configured(error):
        return jsonify(error='Account and order services are not available yet. Please try again later.'), 503

    @application.errorhandler(413)
    def too_large(error):
        return jsonify(error='This request is too large.'), 413

    @application.cli.command('init-db')
    def init_db():
        """Create missing tables and seed the catalog without erasing data."""
        from modules.database import initialize
        initialize(application)
        click.echo('Database ready. Catalog seed applied where needed.')

    @application.cli.command('create-admin')
    @click.option('--email', prompt=True)
    @click.option('--name', default='AUDIA Admin', prompt=True)
    @click.password_option()
    def create_admin(email, name, password):
        """Create an administrator explicitly, with no default password."""
        from modules.auth import validate_email, validate_password
        try:
            email = validate_email(email)
            validate_password(password)
        except ValueError as error:
            raise click.ClickException(str(error)) from error
        if db().query(User).filter_by(email=email).first():
            raise click.ClickException('That email already exists; no account was changed.')
        db().add(User(name=name.strip(), email=email, password_hash=generate_password_hash(password), role='admin'))
        db().commit()
        click.echo('Administrator created.')
    return application


app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', '5000')),
            debug=os.getenv('FLASK_DEBUG', '0') == '1')
