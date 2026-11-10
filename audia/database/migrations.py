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

from sqlalchemy import MetaData, inspect, select, text
from .models import (Order, OrderEvent, OrderPayment, PaymentAttempt, PaymentEvent, Refund,
                     LessonProgress, User, RefundRequest, RequestEvent, Upload, InventoryMovement,
                     Delivery, AccountStatus, Notification, AdminAudit)


def upgrade_database(app):
    """Back up rows/schema, add commerce columns/tables and normalize legacy states.

    Returns the backup path. PostgreSQL DDL uses one transaction; no existing
    records are deleted. Legacy payment states are normalized without inventing
    settlement dates. Duplicate admins abort without choosing an owner.
    """
    engine = app.extensions.get('engine')
    if engine is None:
        raise RuntimeError('Configure the existing database before upgrading.')
    additions = [m.__table__ for m in (OrderEvent, OrderPayment, PaymentAttempt, LessonProgress,
                 PaymentEvent, Refund, RefundRequest, RequestEvent, Upload, InventoryMovement, Delivery, AccountStatus, Notification, AdminAudit)]
    with engine.begin() as connection:
        if connection.dialect.name == 'postgresql':
            connection.execute(text('SELECT pg_advisory_xact_lock(1840329101)'))
        existing = set(inspect(connection).get_table_names())
        admins = connection.execute(select(User.id, User.email).where(User.role == 'admin').order_by(User.id)).all() if 'users' in existing else []
        if len(admins) > 1:
            # Never choose an owner, deactivate an account, or rewrite credentials.
            raise RuntimeError('Multiple administrators exist. Identify the authorized account before applying the single-admin constraint.')
        missing = [table for table in additions if table.name not in existing]
        index = next(index for index in User.__table__.indexes if index.name == 'uq_users_single_admin')
        has_admin_index = any(item['name'] == index.name and item['unique'] for item in inspect(connection).get_indexes('users')) if 'users' in existing else False
        added_columns = []
        for table, names in [(Order.__table__, ('subtotal', 'discount', 'shipping_fee', 'tax', 'channel', 'staff_id')),
                             (PaymentAttempt.__table__, ('manual_review', 'payer_number_masked')),
                             (OrderPayment.__table__, ('amount', 'currency', 'is_simulated', 'receipt_number', 'created_at'))]:
            present = {c['name'] for c in inspect(connection).get_columns(table.name)} if table.name in existing else set()
            if table.name in existing:
                added_columns.extend((table, table.c[name]) for name in names if name not in present)
        needs_status = connection.dialect.name == 'postgresql' and 'order_payments' in existing and any(c['name'] == 'status' and getattr(c['type'], 'length', 24) < 24 for c in inspect(connection).get_columns('order_payments'))
        needs_staff_fk = connection.dialect.name == 'postgresql' and 'orders' in existing and not any(
            fk['constrained_columns'] == ['staff_id'] for fk in inspect(connection).get_foreign_keys('orders'))
        needs_payment_backfill = bool(connection.execute(text(
            'SELECT COUNT(*) FROM orders o LEFT JOIN order_payments p ON p.order_id = o.id WHERE p.order_id IS NULL'
        )).scalar()) if {'orders', 'order_payments'} <= existing else False
        if not missing and not added_columns and not needs_status and not needs_staff_fk and not needs_payment_backfill and has_admin_index:
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
        for table, column in added_columns:
            column_type = column.type.compile(dialect=connection.dialect)
            default = str(column.server_default.arg) if column.server_default is not None else None
            # PostgreSQL cannot add a nonconstant timestamp default safely on all backends.
            if column.name == 'created_at':
                default = None
            clause = f" DEFAULT {default}" if default is not None else ''
            if column.name in ('channel', 'currency'):
                clause = f" DEFAULT '{default}'"
            if column.foreign_keys:
                clause += ' REFERENCES users(id)'
            if not column.nullable and default is not None:
                clause += ' NOT NULL'
            connection.execute(text(f'ALTER TABLE {table.name} ADD COLUMN {column.name} {column_type}{clause}'))
        if needs_status and connection.dialect.name == 'postgresql':
            connection.execute(text('ALTER TABLE order_payments ALTER COLUMN status TYPE VARCHAR(24)'))
        for table in missing:
            table.create(connection, checkfirst=True)
        if needs_staff_fk and not any(c.name == 'staff_id' for _, c in added_columns):
            connection.execute(text('ALTER TABLE orders ADD CONSTRAINT fk_orders_staff FOREIGN KEY (staff_id) REFERENCES users(id)'))
        index.create(connection, checkfirst=True)
        for table in (Order.__table__, OrderPayment.__table__):
            for item in table.indexes:
                item.create(connection, checkfirst=True)
        connection.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_receipt ON order_payments (receipt_number)'))
        # A fulfillment status is never evidence of collection. Older orders without
        # a payment record get an explicit unpaid balance, never a fabricated payment.
        connection.execute(text("""
            INSERT INTO order_payments (order_id, status, reference, amount, currency, is_simulated, created_at)
            SELECT o.id, CASE WHEN o.status IN ('Cancelled', 'Rejected', 'Refunded') THEN 'Cancelled' ELSE 'Pending' END,
                   'TXN-LEGACY-' || o.id, o.total, 'PHP', true, CURRENT_TIMESTAMP
            FROM orders o WHERE NOT EXISTS (SELECT 1 FROM order_payments p WHERE p.order_id = o.id)
        """))
        if added_columns or missing:
            connection.execute(text('UPDATE orders SET subtotal = total WHERE subtotal = 0'))
            connection.execute(text("UPDATE order_payments SET amount = (SELECT total FROM orders WHERE orders.id = order_payments.order_id) WHERE amount = 0"))
            connection.execute(text("UPDATE order_payments SET created_at = (SELECT created_at FROM orders WHERE orders.id = order_payments.order_id) WHERE created_at IS NULL"))
            # Legacy COD was recorded as an offline action; preserve that provenance.
            if any(c.name == 'is_simulated' for _, c in added_columns):
                connection.execute(text("UPDATE order_payments SET is_simulated = false WHERE order_id IN (SELECT id FROM orders WHERE payment = 'Cash on delivery')"))
            connection.execute(text("UPDATE order_payments SET collected_at = (SELECT MAX(completed_at) FROM payment_attempts WHERE payment_attempts.order_id = order_payments.order_id AND status = 'Succeeded') WHERE status = 'Demo paid' AND collected_at IS NULL"))
            connection.execute(text("UPDATE order_payments SET status = 'Paid' WHERE status = 'Demo paid'"))
            connection.execute(text("UPDATE order_payments SET status = 'Refunded' WHERE status = 'Demo refunded'"))
            # Existing refunded records predate the new refund ledger. Preserve their known
            # status without inventing event dates; reporting explicitly flags exclusions.
            connection.execute(text("UPDATE order_payments SET receipt_number = 'RCT-LEGACY-' || order_id WHERE collected_at IS NOT NULL AND status IN ('Paid', 'Refunded') AND receipt_number IS NULL"))
    return backup
