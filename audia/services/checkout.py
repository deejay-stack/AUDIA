"""Shared locked, idempotent order creation for store and administrator POS."""
import re
import secrets
from decimal import Decimal

from sqlalchemy import select, update
from audia.database import db
from audia.database.models import Order, OrderItem, OrderEvent, Product, User, InventoryMovement
from audia.services.ledger import create_payment, money
from audia.services.payments import METHODS


def create_order(data, actor, channel='online'):
    from audia.routes.auth import string
    key = string(data, 'request_key', 80, 16)
    # User lock serializes duplicate submissions, including separate browser tabs.
    db().scalar(select(User).where(User.id == actor.id).with_for_update())
    existing = db().scalar(select(Order).where(Order.user_id == actor.id, Order.request_key == key))
    if existing:
        if existing.channel != channel:
            raise ValueError('This request key already belongs to another sales channel.')
        return existing, False
    if channel == 'pos' and actor.role != 'admin':
        raise ValueError('Only administrators can create counter sales.')
    method = data.get('payment_method', 'cod')
    if not isinstance(method, str) or method not in METHODS or (channel == 'online' and method == 'cash') or (channel == 'pos' and method == 'cod'):
        raise ValueError('Choose a supported payment method for this sales channel.')
    from audia.services.settings import settings
    config = settings()
    if channel == 'online' and method not in config['enabled_methods'].split(','):
        raise ValueError('That payment method is currently unavailable.')
    address = 'Counter pickup' if channel == 'pos' else string(data, 'address', 500, 10)
    phone = '' if channel == 'pos' else string(data, 'phone', 30, 7)
    if channel == 'online' and (not re.fullmatch(r'\+?[\d ()-]+', phone) or not 7 <= len(re.sub(r'\D', '', phone)) <= 15):
        raise ValueError('Enter a valid contact number with 7–15 digits.')
    items = data.get('items')
    if not isinstance(items, list) or not 1 <= len(items) <= 50:
        raise ValueError('A sale must contain between 1 and 50 products.')
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
        raise ValueError('An item is no longer available.')
    order = Order(id='AUD-' + secrets.token_hex(8).upper(), user_id=actor.id,
                  customer=string(data, 'customer', 100, 2) if channel == 'pos' else actor.name,
                  email='' if channel == 'pos' else actor.email, address=address, phone=phone, request_key=key,
                  total=Decimal('0.00'), subtotal=Decimal('0.00'), discount=Decimal('0.00'),
                  tax=Decimal('0.00'), shipping_fee=Decimal('0.00'), status='Pending',
                  channel=channel, staff_id=actor.id if channel == 'pos' else None, payment=METHODS[method])
    for product in products:
        quantity = quantities[product.id]
        # Conditional stock decrement is an additional guard even without row locks.
        changed = db().execute(update(Product).where(Product.id == product.id, Product.active.is_(True),
                              Product.stock >= quantity).values(stock=Product.stock - quantity),
                              execution_options={'synchronize_session': 'fetch'})
        if changed.rowcount != 1:
            raise ValueError(f'{product.name} does not have enough stock. Please update your cart.')
        order.subtotal += product.price * quantity
        order.items.append(OrderItem(product_id=product.id, name=product.name, category=product.category,
                                     quantity=quantity, price=product.price))
    order.subtotal = money(order.subtotal)
    if channel == 'pos':
        order.discount = money(data.get('discount', 0))
        if not 0 <= order.discount < order.subtotal:
            raise ValueError('Discount must be nonnegative and less than the merchandise subtotal.')
        if order.discount:
            reason = string(data, 'discount_reason', 200, 3)
            order.events.append(OrderEvent(status='Pending', kind='discount', note=f'PHP {order.discount}: {reason}', actor_id=actor.id))
    order.total = money(order.subtotal - order.discount + order.tax + order.shipping_fee)
    if channel == 'online':
        order.shipping_fee = money(config['shipping_fee'])
        order.total = money(order.total + order.shipping_fee)
    if 'expected_total' in data and money(data['expected_total']) != order.total:
        raise ValueError('Product prices changed. Refresh and review your cart before ordering.')
    create_payment(order, actor)
    order.events.append(OrderEvent(status='Pending', actor_id=actor.id,
                                  note='Stock reserved. Awaiting internal payment collection.'))
    db().add(order)
    db().flush()
    for product in products:
        db().add(InventoryMovement(product_id=product.id, order_id=order.id, delta=-quantities[product.id],
                                  balance=product.stock, reason='Reserved at checkout', actor_id=actor.id))
    return order, True
