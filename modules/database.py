"""Database connection lifecycle and non-destructive initial schema setup."""
import json
from pathlib import Path
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, Setting


def init_database(app):
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
    if 'db' not in g:
        factory = current_app.extensions.get('db_factory')
        if not factory:
            from werkzeug.exceptions import ServiceUnavailable
            raise ServiceUnavailable('Configure DATABASE_URL first.')
        g.db = factory()
    return g.db


def seed_catalog(app):
    return json.loads((Path(app.root_path) / 'database/catalog.json').read_text(encoding='utf-8'))


def initialize(app):
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
