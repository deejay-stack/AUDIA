"""Module: audia.services.orders.

Purpose: Share validated fulfillment transitions and offline collection auditing.
Main components: TRANSITIONS, update_order.
Related: admin routes, Order/OrderEvent/OrderPayment and auth rollback handling.
Debugging: Callers must lock the Order row; changes commit together in the route.
"""
from sqlalchemy import select
from audia.database import db
from audia.database.models import OrderEvent, Product, InventoryMovement, now

TRANSITIONS = {
    'Pending': ['Confirmed', 'Processing', 'Cancelled', 'Rejected'],
    'Confirmed': ['Processing', 'Cancelled'],
    'Processing': ['Packed', 'Shipped', 'Cancelled'],
    'Packed': ['Shipped', 'Cancelled'],
    'Shipped': ['Out for Delivery', 'Delivered'],
    'Out for Delivery': ['Delivered'],
    'Delivered': ['Returned', 'Refunded'], 'Returned': ['Refunded'], 'Cancelled': [], 'Rejected': [], 'Refunded': [],
}


def update_order(order, data, actor):
    """Validate fulfillment separately from collections/refunds; caller holds order lock."""
    from audia.services.ledger import SETTLED, collect, payment_event, refund, ZERO
    if not any(key in data for key in ('status', 'payment_status')):
        raise ValueError('Choose an order status or record a collection.')
    status = data.get('status', order.status)
    if data.get('expected_status', order.status) != order.status:
        raise ValueError('This order changed. Reopen it and review the current status.')
    if not isinstance(status, str) or status not in TRANSITIONS:
        raise ValueError('Choose a valid order status.')
    changed = status != order.status
    if changed and status not in TRANSITIONS.get(order.status, []):
        raise ValueError('That order status transition is not allowed.')
    record = order.payment_record
    reason = data.get('reason', '')
    if not isinstance(reason, str) or len(reason.strip()) > 250:
        raise ValueError('Enter a short fulfillment or cancellation note (at most 250 characters).')
    paid = record and record.status in SETTLED
    if changed and status in ('Confirmed', 'Processing', 'Packed', 'Shipped', 'Out for Delivery', 'Delivered') and order.payment != 'Cash on delivery' and (not paid or record.status == 'Refunded'):
        raise ValueError('Complete payment before accepting or dispatching this order.')
    if 'payment_status' in data:
        if data['payment_status'] != 'Paid' or order.payment != 'Cash on delivery' or status != 'Delivered':
            raise ValueError('COD collection requires a delivered order.')
        if data.get('collection_confirmed') is not True:
            raise ValueError('Confirm the simulated cash collection.')
        reference = data.get('payment_reference', '')
        if not isinstance(reference, str) or not 3 <= len(reference.strip()) <= 200:
            raise ValueError('Add a collection verification note (3-200 characters).')
        if record is None:
            from audia.services.ledger import create_payment
            create_payment(order, actor)
            record = order.payment_record
        collect(order, actor, 'COD collection confirmed by administrator. ' + reference.strip())
    if not changed:
        return
    if status in ('Cancelled', 'Rejected', 'Refunded') and paid:
        if status == 'Refunded' and data.get('refund_confirmed') is not True:
            raise ValueError('Confirm the internal refund before changing fulfillment status.')
        remaining = ZERO if record.status == 'Refunded' else record.amount - sum((r.amount for r in record.refunds), ZERO)
        if remaining > 0:
            refund(order, {'request_key': 'status-refund-' + order.id,
                          'amount': str(remaining), 'reason': reason.strip() or 'Order ' + status.lower()}, actor)
    elif status in ('Cancelled', 'Rejected') and record:
        payment_event(order, 'Cancelled', 'Order cancelled; no collection.', actor)
    if status in ('Cancelled', 'Rejected'):
        for attempt in order.payment_attempts:
            if attempt.status in ('Pending', 'Awaiting review'):
                attempt.status, attempt.completed_at = 'Cancelled', now()
        # Release reservations only before dispatch. Refunds/returns never auto-restock.
        for item in sorted(order.items, key=lambda item: item.product_id):
            product = db().scalar(select(Product).where(Product.id == item.product_id).with_for_update())
            if product is None:
                raise ValueError('An ordered product is missing.')
            product.stock += item.quantity
            db().add(InventoryMovement(product_id=product.id, order_id=order.id, delta=item.quantity,
                                      balance=product.stock, reason='Reservation released: ' + status, actor_id=actor.id))
    order.status = status
    from audia.services.notifications import notify
    notify(order, 'Order status updated: ' + status + '.')
    order.events.append(OrderEvent(status=status, actor_id=actor.id,
                        note=(reason.strip() or ('Status updated by store.' if actor.role == 'admin' else 'Unpaid order cancelled by customer.'))[:300]))
