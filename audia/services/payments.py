"""Internal payment simulator. No financial service, credential, or money transfer is involved.

Callers lock the owning order before accessing attempts; PostgreSQL serializes
checkout/payment/admin mutations. Request keys survive retries and lost responses.
"""
import secrets
from datetime import timedelta, timezone

from flask import current_app
from audia.database.models import OrderEvent, OrderPayment, PaymentAttempt, now

METHODS = {'cod': 'Cash on delivery', 'gcash': 'GCash', 'maya': 'Maya', 'bpi': 'BPI', 'bdo': 'BDO'}
DEMO_METHODS = set(METHODS.values()) - {'Cash on delivery'}
OUTCOMES = {'success': 'Succeeded', 'failure': 'Failed', 'cancelled': 'Cancelled', 'timeout': 'Timed out'}


def eligible(order):
    if order.payment not in DEMO_METHODS:
        raise ValueError('This order does not use a demo payment method.')
    if order.status != 'Pending' or (order.payment_record and order.payment_record.status != 'Pending'):
        raise ValueError('This order is already settled or is no longer eligible for payment.')


def expired(attempt):
    expiry = attempt.expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    return expiry <= now()


def finish(order, attempt, outcome, actor):
    attempt.status = OUTCOMES[outcome]
    attempt.completed_at = now()
    order.events.append(OrderEvent(status=order.status, kind='payment', actor_id=actor.id,
                                  note=f'Demo {attempt.method} payment {attempt.status.lower()}. Reference: {attempt.id}. No money transferred.'))
    if outcome == 'success':
        if order.payment_record is None:
            order.payment_record = OrderPayment(status='Pending')
        order.payment_record.status = 'Demo paid'
        order.payment_record.reference = attempt.id
        order.status = 'Confirmed'
        order.events.append(OrderEvent(status='Confirmed', actor_id=actor.id,
                                      note='Demo payment confirmed; ready for store processing.'))


def begin_attempt(order, data, actor):
    from audia.routes.auth import string
    key = string(data, 'request_key', 80, 16)
    previous = next((attempt for attempt in order.payment_attempts if attempt.request_key == key), None)
    if previous:
        if previous.status == 'Pending' and expired(previous):
            finish(order, previous, 'timeout', actor)
        return previous
    eligible(order)
    # One active attempt at a time, even across tabs or different request keys.
    for attempt in order.payment_attempts:
        if attempt.status == 'Pending':
            if expired(attempt):
                finish(order, attempt, 'timeout', actor)
            else:
                return attempt
    attempt = PaymentAttempt(id='DEMO-' + secrets.token_hex(16).upper(), request_key=key,
                             method=order.payment, status='Pending', expires_at=now() + timedelta(minutes=10))
    order.payment_attempts.append(attempt)
    return attempt


def confirm_attempt(order, attempt, data, actor):
    outcome = data.get('outcome', 'success')
    if not isinstance(outcome, str) or outcome not in OUTCOMES:
        raise ValueError('Choose a valid demonstration outcome.')
    if outcome in ('failure', 'timeout') and not current_app.config.get('DEMO_PAYMENT_TEST_CONTROLS'):
        raise ValueError('Demo outcome testing controls are disabled on this server.')
    # Exact replay returns the committed result. A different outcome cannot overwrite it.
    if attempt.status != 'Pending':
        return
    eligible(order)
    finish(order, attempt, 'timeout' if expired(attempt) else outcome, actor)
