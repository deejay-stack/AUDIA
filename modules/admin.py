"""Protected inventory, sales, customer, reporting, and store settings endpoints."""
import csv
import io
import json
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
from flask import Blueprint, jsonify, request, Response
from sqlalchemy import select
from .auth import payload, require_user, string, validate_email
from .database import db
from .models import Order, Product, Setting, User, now

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
    columns = ['id', 'customer', 'email', 'product', 'date', 'amount', 'payment', 'status']
    writer = csv.writer(output)
    writer.writerow(columns)
    query, status = request.args.get('q', '').lower(), request.args.get('status', 'All')
    for order in sales_records():
        row = order.public()
        if status != 'All' and row['status'] != status:
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
    status = string(payload(), 'status', 30, 1)
    order = db().scalar(select(Order).where(Order.id == order_id).with_for_update())
    if not order:
        return jsonify(error='Order not found.'), 404
    transitions = {'Pending': ['Processing', 'Cancelled'], 'Processing': ['Shipped', 'Cancelled'],
                   'Shipped': ['Delivered'], 'Delivered': ['Refunded'], 'Cancelled': [], 'Refunded': []}
    if status == order.status:
        return jsonify(order=order.public())
    if status not in transitions.get(order.status, []):
        raise ValueError('That order status transition is not allowed.')
    if status in ('Cancelled', 'Refunded'):
        for item in sorted(order.items, key=lambda item: item.product_id):
            product = db().scalar(select(Product).where(Product.id == item.product_id).with_for_update())
            product.stock += item.quantity
    order.status = status
    db().commit()
    return jsonify(order=order.public())


@admin.get('/products')
@require_user(admin=True)
def products():
    return jsonify(products=[p.public() for p in db().scalars(select(Product).order_by(Product.id))])


def product_values(data):
    values = {key: string(data, key, maximum, minimum) for key, maximum, minimum in (
        ('name', 150, 2), ('brand', 80, 1), ('category', 30, 1), ('level', 30, 1),
        ('color', 60, 0), ('badge', 40, 0), ('image', 2000, 1), ('description', 3000, 1))}
    if values['category'] not in ('Electric', 'Acoustic', 'Bass', 'Classical', 'Accessories', 'Bundles'):
        raise ValueError('Choose a valid product category.')
    if values['level'] not in ('Beginner', 'Intermediate', 'Advanced'):
        raise ValueError('Choose a valid experience level.')
    url = urlparse(values['image'])
    if url.scheme != 'https' or not url.netloc:
        raise ValueError('Use an HTTPS image URL.')
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
    db().commit()
    return jsonify(product=product.public()), 201


@admin.put('/products/<int:product_id>')
@require_user(admin=True)
def edit_product(product_id):
    product = db().scalar(select(Product).where(Product.id == product_id).with_for_update())
    if not product:
        return jsonify(error='Product not found.'), 404
    for key, value in product_values(payload()).items():
        setattr(product, key, value)
    db().commit()
    return jsonify(product=product.public())


@admin.delete('/products/<int:product_id>')
@require_user(admin=True)
def archive_product(product_id):
    product = db().scalar(select(Product).where(Product.id == product_id).with_for_update())
    if not product:
        return jsonify(error='Product not found.'), 404
    product.active = False
    db().commit()
    return jsonify(message='Product archived. Existing order records are preserved.')


@admin.get('/customers')
@require_user(admin=True)
def customers():
    totals = defaultdict(lambda: {'orders': 0, 'amount': 0})
    for order in sales_records():
        totals[order.user_id]['orders'] += 1
        if order.status not in ('Cancelled', 'Refunded'):
            totals[order.user_id]['amount'] += float(order.total)
    return jsonify(customers=[dict(user.public(), **totals[user.id]) for user in
                              db().scalars(select(User).where(User.role == 'customer').order_by(User.created_at.desc()))])


@admin.get('/summary')
@require_user(admin=True)
def summary():
    days = 30 if request.args.get('period') == 'month' else 7
    today = now().date()
    start = today - timedelta(days=days - 1)
    records = [order for order in sales_records() if order.created_at.date() >= start]
    earned = [order for order in records if order.status == 'Delivered']
    by_day, categories = defaultdict(float), defaultdict(float)
    for order in earned:
        by_day[order.created_at.date().isoformat()] += float(order.total)
        for item in order.items:
            categories[item.category] += float(item.price * item.quantity)
    low_stock = list(db().scalars(select(Product).where(Product.active.is_(True), Product.stock <= 4)))
    customers = list(db().scalars(select(User).where(User.role == 'customer')))
    pending = sum(order.status == 'Pending' for order in sales_records())
    return jsonify(gross_revenue=sum(float(order.total) for order in earned), total_orders=len(records),
                   new_customers=sum(user.created_at.date() >= start for user in customers),
                   low_stock_items=len(low_stock), low_stock=[p.public() for p in low_stock], pending_orders=pending,
                   chart=[dict(date=(start + timedelta(days=i)).isoformat(), amount=by_day[(start + timedelta(days=i)).isoformat()])
                          for i in range(days)], categories=dict(categories), period_days=days)


@admin.route('/settings', methods=['GET', 'PUT'])
@require_user(admin=True)
def settings():
    if request.method == 'PUT':
        data = payload()
        name = string(data, 'store_name', 100, 2)
        email = validate_email(data.get('support_email'))
        for key, value in dict(store_name=name, support_email=email).items():
            db().merge(Setting(key=key, value=value))
        db().commit()
    return jsonify(settings={item.key: item.value for item in db().scalars(select(Setting))})
