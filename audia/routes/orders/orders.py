"""Module: audia.routes.orders.orders.

Purpose: Serve order history/details and existing transactional checkout.
Main components: history, detail, checkout.
Related: routes.auth and database User/Product/Order/OrderItem mappings.
Debugging: Trace request_key, locked inventory rows, and validation rollback handling.
"""
import secrets
import re
from decimal import Decimal, InvalidOperation
from flask import Blueprint, g, jsonify
from sqlalchemy import select
from ..auth import payload, require_user, string
from audia.database import db
from audia.database.models import Order, OrderItem, OrderEvent, OrderPayment, Product, User
from audia.services.payments import METHODS, begin_attempt, confirm_attempt

orders = Blueprint('orders', __name__, url_prefix='/api/orders')


@orders.get('')
@require_user(role='customer')
def history():
    items = db().scalars(select(Order).where(Order.user_id == g.user.id).order_by(Order.created_at.desc()))
    return jsonify(orders=[item.public() for item in items])


@orders.get('/<order_id>')
@require_user()
def detail(order_id):
    item = db().get(Order, order_id.upper())
    if not item or (item.user_id != g.user.id and g.user.role != 'admin'):
        return jsonify(error='No order found for this account.'), 404
    return jsonify(order=item.public())


@orders.post('')
@require_user(role='customer')
def checkout():
    """Read the authenticated cart JSON and return the existing order response.

    Uses locked Product/User rows and server prices; ValueError reaches the
    auth validation handler, which rolls back incomplete transactions.
    """
    data = payload()
    key = string(data, 'request_key', 80, 16)
    # Serializes checkouts for the same user, including concurrent retries.
    db().scalar(select(User).where(User.id == g.user.id).with_for_update())
    existing = db().scalar(select(Order).where(Order.user_id == g.user.id, Order.request_key == key))
    if existing:
        return jsonify(order=existing.public()), 200
    method = data.get('payment_method', 'cod')
    if not isinstance(method, str) or method not in METHODS:
        raise ValueError('Choose GCash, Maya, BPI, BDO, or Cash on Delivery.')
    address = string(data, 'address', 500, 10)
    phone = string(data, 'phone', 30, 7)
    if not re.fullmatch(r'\+?[\d ()-]+', phone) or not 7 <= len(re.sub(r'\D', '', phone)) <= 15:
        raise ValueError('Enter a valid contact number with 7–15 digits.')
    items = data.get('items')
    if not isinstance(items, list) or not 1 <= len(items) <= 50:
        raise ValueError('Your cart must contain between 1 and 50 products.')
    quantities = {}
    for item in items:
        if not isinstance(item, dict) or type(item.get('product_id')) is not int or type(item.get('quantity')) is not int:
            raise ValueError('A cart item is invalid.')
        product_id, quantity = item['product_id'], item['quantity']
        if not 1 <= quantity <= 99 or product_id in quantities:
            raise ValueError('Please check the quantities in your cart.')
        quantities[product_id] = quantity
    products = list(db().scalars(select(Product).where(Product.id.in_(quantities)).order_by(Product.id).with_for_update()))
    if len(products) != len(quantities):
        raise ValueError('An item is no longer available. Please update your cart.')
    order = Order(id='AUD-' + secrets.token_hex(6).upper(), user_id=g.user.id, customer=g.user.name,
                  email=g.user.email, address=address, phone=phone, total=Decimal('0'), request_key=key,
                  payment=METHODS[method], payment_record=OrderPayment(status='Pending'))
    order.events.append(OrderEvent(status='Pending', note='Order placed; ' + ('pay with cash on delivery.' if method == 'cod' else 'awaiting demo payment. No money is transferred.'), actor_id=g.user.id))
    for product in products:
        quantity = quantities[product.id]
        if not product.active or product.stock < quantity:
            raise ValueError(f'{product.name} does not have enough stock. Please update your cart.')
        product.stock -= quantity
        order.total += product.price * quantity
        order.items.append(OrderItem(product_id=product.id, name=product.name, category=product.category,
                                     quantity=quantity, price=product.price))
    if 'expected_total' in data:
        try:
            expected = Decimal(str(data['expected_total']))
        except InvalidOperation as error:
            raise ValueError('The checkout total is invalid. Refresh your cart and try again.') from error
        if not expected.is_finite() or expected != order.total:
            raise ValueError('Product prices changed. Refresh your cart and review the updated total before ordering.')
    db().add(order)
    db().commit()
    return jsonify(order=order.public()), 201


def own_locked_order(order_id):
    return db().scalar(select(Order).where(Order.id == order_id.upper(), Order.user_id == g.user.id).with_for_update())


@orders.post('/<order_id>/payment-attempts')
@require_user(role='customer')
def start_payment(order_id):
    order = own_locked_order(order_id)
    if not order:
        return jsonify(error='No order found for this account.'), 404
    attempt = begin_attempt(order, payload(), g.user)
    db().commit()
    from flask import current_app
    return jsonify(order=order.public(), attempt=attempt.public(), test_controls=bool(current_app.config.get('DEMO_PAYMENT_TEST_CONTROLS')))


@orders.post('/<order_id>/payment-attempts/<attempt_id>/confirm')
@require_user(role='customer')
def complete_payment(order_id, attempt_id):
    order = own_locked_order(order_id)
    if not order:
        return jsonify(error='No order found for this account.'), 404
    attempt = next((item for item in order.payment_attempts if item.id == attempt_id), None)
    if not attempt:
        return jsonify(error='Payment attempt not found.'), 404
    confirm_attempt(order, attempt, payload(), g.user)
    db().commit()
    return jsonify(order=order.public(), attempt=attempt.public())


@orders.post('/<order_id>/cancel')
@require_user(role='customer')
def cancel_unpaid_order(order_id):
    order = own_locked_order(order_id)
    if not order:
        return jsonify(error='No order found for this account.'), 404
    if order.status == 'Cancelled':
        return jsonify(order=order.public())
    if order.status != 'Pending' or (order.payment_record and order.payment_record.status != 'Pending'):
        raise ValueError('Only pending, unpaid orders can be cancelled here. Contact the store for assistance.')
    from audia.services.orders import update_order
    update_order(order, {'status': 'Cancelled'}, g.user)
    db().commit()
    return jsonify(order=order.public())
