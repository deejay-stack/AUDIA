"""Locked request/return workflow on top of the existing financial ledger."""
import json
import secrets
from datetime import timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from audia.database import db
from audia.database.models import (RefundRequest, RequestEvent, Upload, Product, InventoryMovement, OrderEvent, now)
from audia.services.ledger import ZERO, money, refund, merchandise_allocations
from audia.services.settings import settings

TERMINAL = {'Rejected', 'Closed', 'Refunded', 'Partially Refunded'}
TRANSITIONS = {
    'Requested': ['Under Review', 'Approved', 'Rejected'],
    'Under Review': ['Approved', 'Rejected'],
    'Approved': ['Awaiting Return', 'Refund Processing'],
    'Awaiting Return': ['Item Received'],
    'Item Received': ['Refund Processing'],
    'Refund Processing': ['Refunded'],
    'Rejected': ['Closed'], 'Refunded': ['Closed'], 'Partially Refunded': ['Closed'], 'Closed': [],
}


def requests_for(order):
    return list(db().scalars(select(RefundRequest).where(RefundRequest.order_id == order.id).order_by(RefundRequest.created_at.desc())))


def request_public(item):
    data = item.public()
    data['evidence'] = [f'/uploads/{u.id}' for u in db().scalars(select(Upload).where(Upload.request_id == item.id))]
    data['next_statuses'] = TRANSITIONS[item.status] + (['Under Review'] if item.status == 'Under Review' else [])
    return data


def request_refund(order, data, actor, kind='refund'):
    from audia.routes.auth import string
    key = string(data, 'request_key', 80, 16)
    existing = next((r for r in requests_for(order) if r.request_key == key), None)
    if existing:
        return existing
    config = settings()
    p = order.payment_record
    if not p or p.status not in ('Paid', 'Partially Refunded') or not p.collected_at:
        raise ValueError('A captured payment is required before requesting a refund.')
    if any(r.status not in TERMINAL for r in requests_for(order)):
        raise ValueError('This order already has an open request. Review its history for updates.')
    reason = string(data, 'reason', 250, 3)
    explanation = string(data, 'explanation', 2000)
    remaining = p.amount - sum((r.amount for r in p.refunds), ZERO)
    selected = []
    if kind == 'cancellation':
        if config['allow_cancellation'] != 'true' or order.status not in ('Pending','Confirmed','Processing','Packed'):
            raise ValueError('This order is no longer eligible for cancellation. Use return/refund after dispatch.')
        amount = remaining
    else:
        if order.status not in ('Shipped','Out for Delivery','Delivered','Returned'):
            raise ValueError('Use cancellation for an unshipped order.')
        delivered = next((e.created_at for e in reversed(order.events) if e.status == 'Delivered' and e.kind == 'status'), None)
        if delivered:
            delivered = delivered.replace(tzinfo=timezone.utc) if delivered.tzinfo is None else delivered
            if now() > delivered + timedelta(days=int(config['return_days'])):
                raise ValueError('The configured return period has ended.')
        lines = data.get('items')
        if not isinstance(lines, list) or not 1 <= len(lines) <= len(order.items):
            raise ValueError('Select the products and quantities to refund.')
        amounts = dict(zip((i.id for i in order.items), merchandise_allocations(order)))
        prior = {}
        for r in requests_for(order):
            if r.refund_id:
                for i in json.loads(r.items_json):
                    prior[i['item_id']] = prior.get(i['item_id'], 0) + i['quantity']
        seen = set()
        amount = ZERO
        for line in lines:
            if not isinstance(line, dict) or type(line.get('item_id')) is not int or type(line.get('quantity')) is not int:
                raise ValueError('Select valid item quantities.')
            item = next((i for i in order.items if i.id == line['item_id']), None)
            qty = line['quantity']
            if not item or item.id in seen or not 1 <= qty <= item.quantity - prior.get(item.id, 0):
                raise ValueError('A quantity exceeds the remaining purchased quantity.')
            seen.add(item.id)
            # Cumulative allocation avoids repeated per-unit rounding beyond the line cap.
            used = prior.get(item.id, 0)
            line_amount = (amounts[item.id] * (used + qty) / item.quantity).quantize(Decimal('.01')) - (amounts[item.id] * used / item.quantity).quantize(Decimal('.01'))
            amount += line_amount
            selected.append(dict(item_id=item.id, product_id=item.product_id, name=item.name, quantity=qty, amount=str(line_amount)))
        amount = min(amount, remaining)
        if config['allow_partial_refunds'] != 'true' and amount != remaining:
            raise ValueError('Store policy permits only full refunds.')
    if amount <= ZERO:
        raise ValueError('No refundable balance remains.')
    item = RefundRequest(id='REQ-' + secrets.token_hex(12).upper(), order_id=order.id, request_key=key,
                         kind=kind, status='Requested', reason=reason, explanation=explanation,
                         destination=config['cod_refund_destination'] if order.payment == 'Cash on delivery' else order.payment,
                         amount=amount, items_json=json.dumps(selected))
    item.events.append(RequestEvent(status='Requested', note=reason, actor_id=actor.id))
    db().add(item)
    db().flush()
    evidence = data.get('evidence', [])
    if not isinstance(evidence, list) or len(evidence) > 4 or any(not isinstance(v, str) for v in evidence):
        raise ValueError('Attach up to four uploaded images.')
    for identifier in sorted(set(evidence)):
        upload = db().scalar(select(Upload).where(Upload.id == identifier).with_for_update())
        if not upload or upload.user_id != actor.id or upload.purpose != 'evidence' or upload.request_id:
            raise ValueError('An evidence image is unavailable or belongs to another request.')
        upload.request_id = item.id
    order.events.append(OrderEvent(status=order.status, kind='refund', note=f'{kind.title()} request {item.id}: {reason}'[:300], actor_id=actor.id))
    from audia.services.notifications import notify
    notify(order, f'{kind.title()} request {item.id} submitted for store review.')
    return item


def review_request(order, item, data, actor):
    from audia.routes.auth import string
    target = string(data, 'status', 24, 3)
    if target == item.status and target == 'Under Review':
        note = string(data, 'note', 300, 3)
        item.events.append(RequestEvent(status=target, note=note, actor_id=actor.id))
        from audia.services.notifications import notify
        notify(order, f'Store review update for {item.id}: {note}')
        return item
    if target == item.status or (item.refund_id and target == 'Refunded'):
        return item
    if target not in TRANSITIONS[item.status]:
        raise ValueError('That request transition is not allowed. Refresh the current request.')
    note = string(data, 'note', 300, 3)
    if item.kind == 'cancellation' and target == 'Approved':
        if order.status not in ('Pending','Confirmed','Processing','Packed'):
            raise ValueError('The order has already dispatched. Review through the return workflow.')
    if target == 'Approved':
        amount = money(data.get('amount', item.amount))
        p = order.payment_record
        remaining = p.amount - sum((r.amount for r in p.refunds), ZERO)
        if not ZERO < amount <= min(item.amount, remaining):
            raise ValueError('Approved refund exceeds the request or remaining collection.')
        if (item.kind == 'cancellation' or settings()['allow_partial_refunds'] != 'true') and amount != remaining:
            raise ValueError('This request requires refunding the full remaining balance.')
        item.approved_amount = amount
    if target == 'Awaiting Return' and item.kind == 'cancellation':
        raise ValueError('Unshipped cancellations do not require a physical return.')
    if target == 'Refund Processing' and item.status == 'Approved' and item.kind != 'cancellation' and settings()['return_required'] == 'true' and item.reason not in ('Missing item', 'Package not received'):
        raise ValueError('Record the returned-item receipt before processing this refund.')
    if target == 'Refunded':
        if item.kind == 'cancellation':
            if order.status not in ('Pending','Confirmed','Processing','Packed'):
                raise ValueError('The order has already dispatched; cancellation cannot be completed.')
            from audia.services.orders import update_order
            # Use a single reversal key shared with the ordinary cancellation service.
            before = {r.id for r in order.payment_record.refunds}
            update_order(order, {'status':'Cancelled', 'reason':item.reason}, actor)
            created = next((r for r in order.payment_record.refunds if r.id not in before), None)
            if not created:
                raise ValueError('No remaining collection can be reversed.')
        else:
            created = refund(order, dict(request_key='request-refund-' + item.id, amount=str(item.approved_amount), reason=item.reason), actor)
        db().flush()
        item.refund_id = created.id
        if item.approved_amount < item.amount:
            target = 'Partially Refunded'
    if data.get('restock') is True:
        if item.kind == 'cancellation' or item.status != 'Item Received' or target != 'Refund Processing' or item.restocked:
            raise ValueError('Restock once, after item receipt and inspection, before refund processing.')
        for line in sorted(json.loads(item.items_json), key=lambda i:i['product_id']):
            product = db().scalar(select(Product).where(Product.id == line['product_id']).with_for_update())
            product.stock += line['quantity']
            db().add(InventoryMovement(product_id=product.id, order_id=order.id, delta=line['quantity'], balance=product.stock,
                                      reason='Inspected return ' + item.id, actor_id=actor.id))
        item.restocked = True
    item.status = target
    item.events.append(RequestEvent(status=target, note=note, actor_id=actor.id))
    order.events.append(OrderEvent(status=order.status, kind='refund', note=f'Request {item.id}: {target}. {note}'[:300], actor_id=actor.id))
    from audia.services.notifications import notify
    notify(order, f'Request {item.id}: {target}. {note}')
    return item
