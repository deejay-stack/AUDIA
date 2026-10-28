"""Module: audia.services.orders.

Purpose: Share validated fulfillment transitions and offline collection auditing.
Main components: TRANSITIONS, update_order.
Related: admin routes, Order/OrderEvent/OrderPayment and auth rollback handling.
Debugging: Callers must lock the Order row; changes commit together in the route.
"""
from sqlalchemy import select
from audia.database import db
from audia.database.models import OrderEvent, OrderPayment, Product, now

TRANSITIONS = {
    'Pending': ['Confirmed', 'Processing', 'Cancelled', 'Rejected'],
    'Confirmed': ['Processing', 'Cancelled'],
    'Processing': ['Shipped', 'Cancelled'],
    'Shipped': ['Out for Delivery', 'Delivered'],
    'Out for Delivery': ['Delivered'],
    'Delivered': ['Refunded'], 'Cancelled': [], 'Rejected': [], 'Refunded': [],
}


def update_order(order, data, actor):
    """Apply validated status/collection input to a locked order; return None.

    Raises ValueError before commit for invalid transitions or unverified payment.
    Existing legacy status shortcuts stay valid; repeated updates are idempotent.
    """
    if not any(key in data for key in ('status', 'payment_status')):
        raise ValueError('Choose an order status or record a collected payment.')
    status = data.get('status', order.status)
    if data.get('expected_status', order.status) != order.status:
        raise ValueError('This order changed since you opened it. Close it and review the latest status.')
    if not isinstance(status, str) or status not in TRANSITIONS:
        raise ValueError('Choose a valid order status.')
    changed = status != order.status
    if changed and status not in TRANSITIONS.get(order.status, []):
        raise ValueError('That order status transition is not allowed.')
    payment = data.get('payment_status')
    record = order.payment_record
    if changed and status in ('Confirmed', 'Processing', 'Shipped', 'Out for Delivery', 'Delivered') and order.payment != 'Cash on delivery':
        raise ValueError('This payment method is not connected. Unverified preview payments cannot be accepted or dispatched.')
    if 'payment_status' in data:
        if payment != 'Paid':
            raise ValueError('Payment can only be recorded after actual collection.')
        if order.payment != 'Cash on delivery':
            raise ValueError('Demo or unsupported payment methods cannot be verified as real payments.')
        if status != 'Delivered':
            raise ValueError('Record COD collection only when delivery has been completed.')
        if data.get('collection_confirmed') is not True:
            raise ValueError('Confirm that the cash payment was actually collected.')
        reference = data.get('payment_reference', '')
        if not isinstance(reference, str) or not 3 <= len(reference.strip()) <= 200:
            raise ValueError('Add a collection receipt or verification note (3–200 characters).')
        if record is None or record.status != 'Paid':
            if record is None:
                record = OrderPayment(status='Pending')
                order.payment_record = record
            record.status = 'Paid'
            record.reference = reference.strip()
            record.collected_at = now()
            record.collected_by = actor.id
            order.events.append(OrderEvent(status=status, kind='payment', note='Cash collection recorded by the store.', actor_id=actor.id))
    if changed:
        if status in ('Cancelled', 'Rejected', 'Refunded'):
            for item in sorted(order.items, key=lambda item: item.product_id):
                product = db().scalar(select(Product).where(Product.id == item.product_id).with_for_update())
                if product is None:
                    raise ValueError('An ordered product is missing. Contact store support.')
                product.stock += item.quantity
        if status == 'Refunded' and record and record.status == 'Paid':
            if data.get('refund_confirmed') is not True:
                raise ValueError('Confirm the offline refund was completed before marking a paid order refunded.')
            record.status = 'Refunded'
            order.events.append(OrderEvent(status=status, kind='payment', note='Offline refund confirmed by the store.', actor_id=actor.id))
        order.status = status
        order.events.append(OrderEvent(status=status, kind='status', note='Status updated by the store.', actor_id=actor.id))
