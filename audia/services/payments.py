"""Internal payment simulator. No financial service, credential, or money transfer is involved.

Callers lock the owning order before accessing attempts; PostgreSQL serializes
checkout/payment/admin mutations. Request keys survive retries and lost responses.
"""
import secrets
import re
from datetime import timedelta, timezone

from flask import current_app
from audia.database.models import OrderEvent, PaymentAttempt, now

METHODS = {'cod': 'Cash on delivery', 'gcash': 'GCash', 'maya': 'Maya', 'bpi': 'BPI', 'bdo': 'BDO', 'metrobank': 'Metrobank', 'landbank': 'LandBank', 'cash': 'Cash'}
DEMO_METHODS = set(METHODS.values()) - {'Cash on delivery', 'Cash'}
OUTCOMES = {'success': 'Succeeded', 'failure': 'Failed', 'cancelled': 'Cancelled', 'timeout': 'Timed out'}


def eligible(order):
    if order.payment not in DEMO_METHODS:
        raise ValueError('This order does not use an online payment method.')
    if order.status != 'Pending' or (order.payment_record and order.payment_record.status not in ('Pending', 'Processing', 'Failed', 'Cancelled')):
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
                                  note=f'Internal {attempt.method} payment {attempt.status.lower()}. Reference: {attempt.id}. No money transferred.'))
    from audia.services.ledger import collect, payment_event
    if outcome == 'success':
        if attempt.manual_review:
            attempt.status = 'Awaiting review'
            payment_event(order, 'Pending Verification', f'Internal bank authorization {attempt.id} awaits administrator verification.', actor)
            return
        collect(order, actor, f'Internal {attempt.method} simulation confirmed. Attempt: {attempt.id}. No funds transferred.')
        order.status = 'Confirmed'
        order.events.append(OrderEvent(status='Confirmed', actor_id=actor.id,
                                      note='Internal test payment confirmed; ready for store processing.'))
    else:
        payment_event(order, 'Failed' if outcome in ('failure', 'timeout') else 'Cancelled',
                      f'Payment attempt {attempt.id}: {attempt.status}.', actor)


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
    attempt = PaymentAttempt(id='PAY-' + secrets.token_hex(16).upper(), request_key=key,
                             method=order.payment, status='Pending', expires_at=now() + timedelta(minutes=10))
    from audia.services.settings import settings, BANKS
    attempt.manual_review = order.channel == 'online' and order.payment in BANKS and settings()['bank_mode'] == 'manual'
    order.payment_attempts.append(attempt)
    from audia.services.ledger import payment_event
    payment_event(order, 'Processing', f'Internal payment attempt {attempt.id} started.', actor)
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
    if outcome == 'success' and order.channel == 'online' and order.payment == 'GCash' and not expired(attempt):
        number = data.get('gcash_number', '')
        if not isinstance(number, str):
            raise ValueError('Enter a valid GCash mobile number (09XXXXXXXXX or +639XXXXXXXXX).')
        number = re.sub(r'[\s-]', '', number)
        if not re.fullmatch(r'(?:09\d{9}|\+639\d{9})', number):
            raise ValueError('Enter a valid GCash mobile number (09XXXXXXXXX or +639XXXXXXXXX).')
        local_number = '0' + number[3:] if number.startswith('+63') else number
        attempt.payer_number_masked = '09•••••' + local_number[-4:]
    finish(order, attempt, 'timeout' if expired(attempt) else outcome, actor)


def verify_bank(order, data, actor):
    """Manual review consumes only an authorized pending bank attempt under order lock."""
    from audia.services.ledger import payment_event, collect
    from audia.routes.auth import string
    action = data.get('action')
    if action not in ('approve', 'reject'):
        raise ValueError('Choose approve or reject.')
    note = string(data, 'note', 180, 3)
    attempt = next((a for a in reversed(order.payment_attempts) if a.status in ('Awaiting review', 'Verified', 'Rejected')), None)
    if not attempt or data.get('attempt_id') != attempt.id:
        raise ValueError('Select the current bank authorization to review.')
    if attempt.status != 'Awaiting review':
        return
    if order.payment_record.status != 'Pending Verification' or order.status != 'Pending':
        raise ValueError('This order no longer has a reviewable payment.')
    attempt.completed_at = now()
    if action == 'approve':
        # collect accepts a review state only through this authorized service.
        payment_event(order, 'Processing', 'Bank simulation reviewed: ' + note, actor)
        collect(order, actor, 'Administrator approved internal bank simulation. ' + note)
        attempt.status = 'Verified'
        order.status = 'Confirmed'
        order.events.append(OrderEvent(status='Confirmed', actor_id=actor.id, note='Manually verified simulated bank payment.'))
    else:
        attempt.status = 'Rejected'
        payment_event(order, 'Failed', 'Administrator rejected internal bank simulation. ' + note, actor)
