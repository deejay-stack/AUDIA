"""Module: audia.routes.orders.orders.

Purpose: Serve order history/details and existing transactional checkout.
Main components: history, detail, checkout.
Related: routes.auth and database User/Product/Order/OrderItem mappings.
Debugging: Trace request_key, locked inventory rows, and validation rollback handling.
"""
from flask import Blueprint, g, jsonify
from sqlalchemy import select
from ..auth import payload, require_user, string
from audia.database import db
from audia.database.models import Order
from audia.services.payments import begin_attempt, confirm_attempt

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
    from audia.services.checkout import create_order
    order, created = create_order(payload(), g.user)
    db().commit()
    return jsonify(order=order.public()), 201 if created else 200


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
    from audia.services.settings import payment_profile
    return jsonify(order=order.public(), attempt=attempt.public(), profile=payment_profile(order), test_controls=bool(current_app.config.get('DEMO_PAYMENT_TEST_CONTROLS')))


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
    data = payload()
    from audia.services.settings import settings
    if settings()['allow_cancellation'] != 'true':
        raise ValueError('Order cancellation is disabled by current store policy.')
    if order.payment_record and order.payment_record.status in ('Paid', 'Partially Refunded'):
        from audia.services.returns import request_refund, request_public
        item = request_refund(order, data, g.user, kind='cancellation')
        db().commit()
        return jsonify(order=order.public(), request=request_public(item))
    if order.status not in ('Pending', 'Confirmed', 'Processing', 'Packed'):
        raise ValueError('Dispatched orders use the return/refund workflow.')
    from audia.services.orders import update_order
    reason = string(data, 'reason', 250) or 'Customer cancelled unpaid order.'
    update_order(order, {'status': 'Cancelled', 'reason':reason}, g.user)
    db().commit()
    return jsonify(order=order.public())
