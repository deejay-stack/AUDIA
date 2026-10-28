"""Module: audia.routes.orders.orders.

Purpose: Serve order history/details and existing transactional checkout.
Main components: history, detail, checkout.
Related: routes.auth and database User/Product/Order/OrderItem mappings.
Debugging: Trace request_key, locked inventory rows, and validation rollback handling.
"""
import secrets
from decimal import Decimal
from flask import Blueprint, g, jsonify
from sqlalchemy import select
from ..auth import payload, require_user, string
from audia.database import db
from audia.database.models import Order, OrderItem, OrderEvent, OrderPayment, Product, User

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
    # Demo payment cards are previews. Only the existing COD workflow places orders.
    if data.get('payment_method', 'cod') != 'cod':
        raise ValueError('Card and e-wallet options are previews only. Choose Cash on Delivery to place an order.')
    address = string(data, 'address', 500, 10)
    phone = string(data, 'phone', 30, 7)
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
                  payment='Cash on delivery', payment_record=OrderPayment(status='Pending'))
    order.events.append(OrderEvent(status='Pending', note='Order placed; awaiting store confirmation.', actor_id=g.user.id))
    for product in products:
        quantity = quantities[product.id]
        if not product.active or product.stock < quantity:
            raise ValueError(f'{product.name} does not have enough stock. Please update your cart.')
        product.stock -= quantity
        order.total += product.price * quantity
        order.items.append(OrderItem(product_id=product.id, name=product.name, category=product.category,
                                     quantity=quantity, price=product.price))
    db().add(order)
    db().commit()
    return jsonify(order=order.public()), 201
