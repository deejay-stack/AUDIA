"""Module: audia.database.migrations.

Purpose: Add commerce tables and a single-admin index without rewriting existing records.
Main components: upgrade_database.
Related: database.models and the root upgrade-db CLI command.
Debugging: Inspect the private pre-migration backup and PostgreSQL DDL errors.
"""
import gzip
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import MetaData, inspect, select
from .models import OrderEvent, OrderPayment, LessonProgress, User


def upgrade_database(app):
    """Back up existing rows/schema, then create missing tables and the admin index.

    Returns the backup path. PostgreSQL DDL uses one transaction; no existing
    columns or records change. Duplicate admins abort without choosing an owner.
    """
    engine = app.extensions.get('engine')
    if engine is None:
        raise RuntimeError('Configure the existing database before upgrading.')
    additions = [OrderEvent.__table__, OrderPayment.__table__, LessonProgress.__table__]
    with engine.begin() as connection:
        if connection.dialect.name == 'postgresql':
            from sqlalchemy import text
            connection.execute(text('SELECT pg_advisory_xact_lock(1840329101)'))
        existing = set(inspect(connection).get_table_names())
        admins = connection.execute(select(User.id, User.email).where(User.role == 'admin').order_by(User.id)).all() if 'users' in existing else []
        if len(admins) > 1:
            # Never choose an owner, deactivate an account, or rewrite credentials.
            raise RuntimeError('Multiple administrators exist. Identify the authorized account before applying the single-admin constraint.')
        missing = [table for table in additions if table.name not in existing]
        index = next(index for index in User.__table__.indexes if index.name == 'uq_users_single_admin')
        has_admin_index = any(item['name'] == index.name and item['unique'] for item in inspect(connection).get_indexes('users')) if 'users' in existing else False
        if not missing and has_admin_index:
            return None
        if not {'orders', 'users', 'products'} <= existing:
            raise RuntimeError('Initialize the existing application database before upgrade-db.')
        metadata = MetaData()
        metadata.reflect(bind=connection)
        snapshot = {table.name: {
            'columns': [{'name': column.name, 'type': str(column.type)} for column in table.columns],
            'rows': [dict(row) for row in connection.execute(select(table)).mappings()],
        } for table in metadata.sorted_tables}
        folder = Path(app.instance_path) / 'backups'
        folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = folder / f'database-before-upgrade-{stamp}.json.gz'
        with gzip.open(backup, 'xt', encoding='utf-8') as archive:
            json.dump(snapshot, archive, default=str)
        for table in missing:
            table.create(connection, checkfirst=True)
        index.create(connection, checkfirst=True)
    return backup
