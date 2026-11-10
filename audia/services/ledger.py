"""One internal collection/refund ledger for online and counter sales.

Mutations require the caller to lock the order and commit the whole transaction.
Money stays Decimal until JSON serialization. No external provider is called.
"""
import secrets
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, ROUND_DOWN

from audia.database.models import OrderPayment, PaymentEvent, Refund, now

ZERO = Decimal('0.00')
SETTLED = {'Paid', 'Partially Refunded', 'Refunded'}
UNPAID = {'Pending', 'Processing', 'Failed', 'Cancelled'}


def merchandise_allocations(order):
    """Allocate discounted merchandise in centavos using largest remainders.

    Independent per-line rounding can produce a negative last line when a large
    discount leaves only a few centavos across many products.
    """
    total = order.subtotal - order.discount
    raw = [item.price * item.quantity * total / order.subtotal for item in order.items]
    allocated = [value.quantize(Decimal('.01'), rounding=ROUND_DOWN) for value in raw]
    remaining = int((total - sum(allocated, ZERO)) * 100)
    for index in sorted(range(len(raw)), key=lambda i: (-(raw[i] - allocated[i]), i))[:remaining]:
        allocated[index] += Decimal('.01')
    return allocated


def money(value):
    try:
        result = Decimal(str(value))
        if not result.is_finite() or abs(result) > Decimal('9999999999.99') or result != result.quantize(Decimal('.01')):
            raise ValueError
        return result.quantize(Decimal('.01'))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise ValueError('Enter a valid amount with at most two decimal places.') from error


def payment_event(order, status, action, actor):
    record = order.payment_record
    record.events.append(PaymentEvent(previous_status=record.status, new_status=status,
                                      action=action, actor_id=actor.id if actor else None))
    record.status = status


def create_payment(order, actor):
    order.payment_record = OrderPayment(status='Pending', amount=order.total, currency='PHP',
                                        reference='TXN-' + secrets.token_hex(12).upper(), is_simulated=True)
    payment_event(order, 'Pending', 'Internal test payment created; no funds transferred.', actor)


def collect(order, actor, action):
    record = order.payment_record
    if record.status in SETTLED:
        return
    if record.status not in UNPAID or order.status in ('Cancelled', 'Rejected', 'Returned'):
        raise ValueError('This order cannot be collected.')
    record.amount = order.total
    record.is_simulated = True
    record.collected_at = now()
    record.collected_by = actor.id
    record.receipt_number = 'RCT-' + secrets.token_hex(12).upper()
    payment_event(order, 'Paid', action, actor)
    from audia.services.notifications import notify
    notify(order, f'Payment recorded: PHP {record.amount}. Your store receipt is ready. No funds transferred.')


def refund(order, data, actor):
    from audia.routes.auth import string
    record = order.payment_record
    key = string(data, 'request_key', 80, 16)
    previous = next((r for r in record.refunds if r.request_key == key), None) if record else None
    if previous:
        return previous
    if not record or record.status not in ('Paid', 'Partially Refunded'):
        raise ValueError('Only collected payments can be refunded.')
    amount = money(data.get('amount'))
    reason = string(data, 'reason', 300, 3)
    refunded = sum((r.amount for r in record.refunds), ZERO)
    remaining = record.amount - refunded
    if not ZERO < amount <= remaining:
        raise ValueError('Refund must be positive and cannot exceed the remaining collected amount.')
    from audia.services.settings import settings
    if settings()['allow_partial_refunds'] != 'true' and amount != remaining:
        raise ValueError('Store policy permits only full refunds.')
    # Proportional allocation to merchandise; final refund absorbs centavo rounding.
    merchandise = order.subtotal - order.discount
    prior_merchandise = sum((r.merchandise_amount for r in record.refunds), ZERO)
    merchandise_amount = merchandise - prior_merchandise if amount == remaining else (
        amount * merchandise / record.amount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    merchandise_amount = min(amount, merchandise - prior_merchandise, merchandise_amount)
    item = Refund(id='REF-' + secrets.token_hex(12).upper(), request_key=key, amount=amount,
                  merchandise_amount=merchandise_amount, reason=reason, actor_id=actor.id)
    record.refunds.append(item)
    payment_event(order, 'Refunded' if amount == remaining else 'Partially Refunded',
                  f'Internal refund {item.id}: PHP {amount}. {reason} No funds transferred.', actor)
    from audia.services.notifications import notify
    notify(order, f'Refund recorded: PHP {amount}. Reference {item.id}. No funds transferred.')
    return item
