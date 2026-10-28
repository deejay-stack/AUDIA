"""Module: audia.database.connection.

Purpose: Manage engines, request-scoped sessions, and existing catalog initialization.
Main components: init_database, db, seed_catalog, initialize.
Related: database.models, app.py configuration, root database/catalog.json.
Debugging: Check DATABASE_URL and engine creation; request sessions close at teardown.
"""
import json
from pathlib import Path
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, Setting


def init_database(app):
    """Configure app engine/session factories and teardown; return None.

    Reads DATABASE_URL without connecting eagerly. Unsupported production
    drivers raise ValueError; database failures surface when queries execute.
    """
    url = app.config['DATABASE_URL']
    if url:
        url = make_url(url)
        if url.drivername in ('postgres', 'postgresql'):
            url = url.set(drivername='postgresql+psycopg')
        if not app.testing and url.drivername != 'postgresql+psycopg':
            raise ValueError('DATABASE_URL must point to PostgreSQL.')
        engine = create_engine(url, pool_pre_ping=True)
        app.extensions['engine'] = engine
        app.extensions['db_factory'] = sessionmaker(engine, expire_on_commit=False)

    @app.teardown_appcontext
    def close_session(error=None):
        connection = g.pop('db', None)
        if connection is not None:
            connection.close()


def db():
    """Return the current Flask context SQLAlchemy session.

    Creates it from the configured factory on first use; raises
    ServiceUnavailable when database configuration is absent.
    """
    if 'db' not in g:
        factory = current_app.extensions.get('db_factory')
        if not factory:
            from werkzeug.exceptions import ServiceUnavailable
            raise ServiceUnavailable('Configure DATABASE_URL first.')
        g.db = factory()
    return g.db


def seed_catalog(app):
    """Return catalog records loaded from the root seed JSON for app.

    Called by initialization and catalog fallback; file/JSON errors propagate
    so missing resource paths can be diagnosed at the caller.
    """
    return json.loads((Path(app.root_path) / 'database/catalog.json').read_text(encoding='utf-8'))


def initialize(app):
    """Initialize missing tables and empty catalog/settings for app; return None.

    Uses the configured engine and seed_catalog(); existing records stay
    intact. Missing configuration or SQL failures propagate to the caller.
    """
    engine = app.extensions.get('engine')
    if engine is None:
        raise RuntimeError('Set DATABASE_URL in .env before initializing the database.')
    Base.metadata.create_all(engine)
    with app.app_context():
        if not db().query(Product).first():
            for item in seed_catalog(app):
                item.pop('id')
                item['specs'] = json.dumps(item['specs'])
                db().add(Product(**item))
        for key, value in {'store_name': 'AUDIA Flagship', 'support_email': 'support@audia.ph'}.items():
            if db().get(Setting, key) is None:
                db().add(Setting(key=key, value=value))
        db().commit()
