"""Module: audia.routes.admin.admin.

Purpose: Serve protected inventory, sales, customer, reporting, and settings APIs.
Main components: sales_records, sales, export_sales, update_order, products, product_values, add_product, edit_product, archive_product, customers, summary, settings.
Related: routes.auth validation/authorization and audia.database models.
Debugging: Check require_user(admin=True), product_values(), and order transitions.
"""
import csv
import io
import json
from pathlib import Path
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
from flask import Blueprint, current_app, g, jsonify, request, Response
from sqlalchemy import select
from ..auth import payload, require_user, string, validate_email
from audia.database import db
from audia.database.models import Order, Product, Setting, User, InventoryMovement, Upload, RefundRequest, AdminAudit, OrderEvent, now
from audia.services.orders import update_order as apply_order_update

admin = Blueprint('admin', __name__, url_prefix='/api/admin')


def sales_records():
    return list(db().scalars(select(Order).order_by(Order.created_at.desc())))


@admin.get('/sales')
@require_user(admin=True)
def sales():
    items = [order.public() for order in sales_records()]
    return jsonify(sales=items, count=len(items))


@admin.get('/sales/export')
@require_user(admin=True)
def export_sales():
    output = io.StringIO(newline='')
    columns = ['id', 'customer', 'email', 'product', 'date', 'amount', 'payment', 'payment_status', 'is_demo', 'status']
    writer = csv.writer(output)
    writer.writerow(columns)
    query, status = request.args.get('q', '').lower(), request.args.get('status', 'All')
    for order in sales_records():
        row = order.public()
        if status != 'All' and row['status'] != status:
            continue
        if request.args.get('payment_status') and row['payment_status'] != request.args['payment_status']:
            continue
        if query not in ' '.join(str(row[key]) for key in ('id', 'customer', 'email', 'product')).lower():
            continue
        # Neutralize spreadsheet formulas in user-controlled cells.
        values = [str(row[key]) for key in columns]
        writer.writerow(["'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value for value in values])
    return Response('\ufeff' + output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename="audia-sales.csv"'})


@admin.patch('/sales/<order_id>')
@require_user(admin=True)
def update_order(order_id):
    """Apply the requested status to order_id and return its public JSON.

    Uses the existing allowed transitions and inventory locks; invalid
    transitions raise ValueError for the shared rollback handler.
    """
    data = payload()
    order = db().scalar(select(Order).where(Order.id == order_id).with_for_update())
    if not order:
        return jsonify(error='Order not found.'), 404
    apply_order_update(order, data, g.user)
    db().commit()
    return jsonify(order=order.public())


@admin.get('/products')
@require_user(admin=True)
def products():
    return jsonify(products=[p.public() for p in db().scalars(select(Product).order_by(Product.id))])


def product_values(data):
    """Convert input product data to validated model values.

    Returns a mapping for add/edit handlers; invalid prices, stock, or image
    references raise ValueError for the shared rollback/error handler.
    """
    values = {key: string(data, key, maximum, minimum) for key, maximum, minimum in (
        ('name', 150, 2), ('brand', 80, 1), ('category', 30, 1), ('level', 30, 1),
        ('color', 60, 0), ('badge', 40, 0), ('image', 2000, 1), ('description', 3000, 1))}
    from audia.services.settings import settings
    if values['category'] not in settings()['categories'].split(','):
        raise ValueError('Choose a valid product category.')
    if values['level'] not in ('Beginner', 'Intermediate', 'Advanced'):
        raise ValueError('Choose a valid experience level.')
    url = urlparse(values['image'])
    is_local = False
    if values['image'].startswith('/static/images/'):
        image_root = (Path(current_app.static_folder) / 'images').resolve()
        local_image = (image_root / values['image'].removeprefix('/static/images/')).resolve()
        is_local = (local_image.is_relative_to(image_root) and local_image.is_file()
                    and local_image.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.svg'))
    is_upload = values['image'].startswith('/uploads/') and db().scalar(select(Upload.id).where(Upload.id == values['image'].removeprefix('/uploads/'), Upload.purpose == 'product')) is not None
    if not is_local and not is_upload and (url.scheme != 'https' or not url.netloc):
        raise ValueError('Use an HTTPS image URL or an existing /static/images/ file.')
    try:
        price = Decimal(str(data.get('price')))
    except InvalidOperation as error:
        raise ValueError('Enter a valid price.') from error
    if not price.is_finite() or not 0 < price <= 10000000 or price != price.quantize(Decimal('.01')):
        raise ValueError('Enter a positive price with at most two decimal places.')
    stock = data.get('stock')
    if type(stock) is not int or not 0 <= stock <= 100000:
        raise ValueError('Stock must be a whole number between 0 and 100,000.')
    specs = data.get('specs', [])
    if not isinstance(specs, list) or len(specs) > 20 or any(not isinstance(s, str) or len(s) > 200 for s in specs):
        raise ValueError('Enter up to 20 short specifications.')
    values.update(price=price, stock=stock, specs=json.dumps(specs), active=data.get('active', True) is True)
    return values


@admin.post('/products')
@require_user(admin=True)
def add_product():
    product = Product(**product_values(payload()))
    db().add(product)
    db().flush()
    db().add(InventoryMovement(product_id=product.id, delta=product.stock, balance=product.stock, reason='Product created', actor_id=g.user.id))
    db().add(AdminAudit(actor_id=g.user.id, action=f'Created product #{product.id}.'))
    db().commit()
    return jsonify(product=product.public()), 201


@admin.put('/products/<int:product_id>')
@require_user(admin=True)
def edit_product(product_id):
    product = db().scalar(select(Product).where(Product.id == product_id).with_for_update())
    if not product:
        return jsonify(error='Product not found.'), 404
    previous_stock = product.stock
    for key, value in product_values(payload()).items():
        setattr(product, key, value)
    db().add(AdminAudit(actor_id=g.user.id, action=f'Updated product #{product.id}.'))
    if previous_stock != product.stock:
        db().add(InventoryMovement(product_id=product.id, delta=product.stock-previous_stock, balance=product.stock,
                                  reason='Administrator stock adjustment', actor_id=g.user.id))
    db().commit()
    return jsonify(product=product.public())


@admin.delete('/products/<int:product_id>')
@require_user(admin=True)
def archive_product(product_id):
    product = db().scalar(select(Product).where(Product.id == product_id).with_for_update())
    if not product:
        return jsonify(error='Product not found.'), 404
    product.active = False
    db().add(AdminAudit(actor_id=g.user.id, action=f'Archived product #{product.id}.'))
    db().commit()
    return jsonify(message='Product archived. Existing order records are preserved.')


@admin.get('/customers')
@require_user(admin=True)
def customers():
    totals = defaultdict(lambda: {'orders': 0, 'amount': Decimal('0.00')})
    for order in sales_records():
        totals[order.user_id]['orders'] += 1
        if order.payment_record and order.payment_record.status in ('Paid', 'Partially Refunded'):
            totals[order.user_id]['amount'] += order.total - sum((r.amount for r in order.payment_record.refunds), Decimal('0'))
    return jsonify(customers=[dict(user.public(), orders=totals[user.id]['orders'], amount=float(totals[user.id]['amount'])) for user in
                              db().scalars(select(User).where(User.role == 'customer').order_by(User.created_at.desc()))])


@admin.get('/summary')
@require_user(admin=True)
def summary():
    from audia.services.reporting import report, in_range, date_range
    data = report(sales_records(), request.args)
    start, end = date_range(request.args)
    low_stock = list(db().scalars(select(Product).where(Product.active.is_(True), Product.stock <= 4)))
    customers = list(db().scalars(select(User).where(User.role == 'customer')))
    requests = list(db().scalars(select(RefundRequest)))
    return jsonify(**data, new_customers=sum(in_range(u.created_at, start, end) for u in customers),
                   recent_activity=[dict(e.public(),order_id=e.order_id) for e in db().scalars(select(OrderEvent).order_by(OrderEvent.created_at.desc()).limit(8))],
                   refund_requests=sum(r.status not in ('Rejected','Closed','Refunded','Partially Refunded') for r in requests),
                   completed_refunds=sum(r.refund_id is not None for r in requests),
                   verification_pending=sum(o.payment_record is not None and o.payment_record.status == 'Pending Verification' for o in sales_records()),
                   low_stock_items=len(low_stock), low_stock=[p.public() for p in low_stock],
                   pending_orders=sum(o.status == 'Pending' for o in sales_records()))


@admin.route('/settings', methods=['GET', 'PUT'])
@require_user(admin=True)
def settings():
    from audia.services.settings import settings as store_settings, save_settings
    if request.method == 'PUT':
        data = payload()
        save_settings(data)
        db().add(AdminAudit(actor_id=g.user.id, action='Updated store settings: ' + ', '.join(sorted(data))[:275]))
        db().commit()
    return jsonify(settings=store_settings())
