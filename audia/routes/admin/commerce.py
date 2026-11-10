"""Protected POS, transaction ledger, refunds, reports and internal receipts."""
import csv
import io

from flask import Blueprint, g, jsonify, request, Response, render_template, abort, url_for
from sqlalchemy import select
from audia.database import db
from audia.database.models import Order, Setting, OrderPayment, Refund, RefundRequest
from audia.routes.auth import require_user, require_page, payload
from audia.services.checkout import create_order
from audia.services.ledger import collect, refund, SETTLED, ZERO
from audia.services.payments import begin_attempt, confirm_attempt
from audia.services.reporting import report, transaction, date_range, in_range

commerce = Blueprint('commerce', __name__)


def records():
    return list(db().scalars(select(Order).order_by(Order.created_at.desc())))


@commerce.post('/api/admin/pos')
@require_user(admin=True)
def counter_sale():
    data = payload()
    if data.get('confirmed') is not True:
        raise ValueError('Confirm the internal test transaction before collecting payment.')
    order, created = create_order(data, g.user, 'pos')
    if created:
        if order.payment == 'Cash':
            collect(order, g.user, 'Counter cash test collection confirmed. No funds transferred.')
        else:
            attempt = begin_attempt(order, {'request_key': data['request_key']}, g.user)
            confirm_attempt(order, attempt, {'outcome': 'success'}, g.user)
        from audia.database.models import OrderEvent
        order.status = 'Delivered'
        order.events.append(OrderEvent(status='Delivered', actor_id=g.user.id, note='Counter purchase collected by customer.'))
    db().commit()
    return jsonify(order=order.public()), 201 if created else 200


@commerce.get('/api/admin/transactions')
@commerce.get('/api/admin/transactions/export')
@require_user(admin=True)
def transactions():
    orders = records()
    start, end = date_range(request.args)
    metric = request.args.get('metric')
    supported_metrics = {'revenue', 'gross_sales', 'net_sales', 'collected_total', 'refunded_total', 'paid_orders', 'products_sold', 'pending_collection', 'refunded_transactions'}
    if metric and metric not in supported_metrics:
        raise ValueError('Choose a supported revenue metric.')
    supports = set(report(orders, request.args)['supporting_orders']) if metric in ('revenue', 'net_sales') else None
    query = request.args.get('q', '').casefold()
    rows = []
    for order in orders:
        p = order.payment_record
        if not p:
            continue
        collection_in_period = p.status in SETTLED and in_range(p.collected_at, start, end) and not (p.status == 'Refunded' and not p.refunds)
        refund_in_period = any(in_range(r.created_at, start, end) for r in p.refunds)
        pending_in_period = p.status not in SETTLED and order.status not in ('Cancelled', 'Rejected') and in_range(order.created_at, start, end)
        if metric in ('gross_sales', 'collected_total', 'paid_orders', 'products_sold') and not collection_in_period:
            continue
        if metric in ('refunded_total', 'refunded_transactions') and not refund_in_period:
            continue
        if metric == 'pending_collection' and not pending_in_period:
            continue
        if supports is not None:
            if order.id not in supports:
                continue
        elif metric != 'pending_collection' and not (in_range(p.collected_at or p.created_at, start, end) or any(in_range(r.created_at, start, end) for r in p.refunds)):
            continue
        row = transaction(order)
        row['collection_in_period'] = float(p.amount) if collection_in_period else 0
        row['refunds_in_period'] = float(sum((r.amount for r in p.refunds if in_range(r.created_at, start, end)), 0))
        row['net_collection_in_period'] = float((p.amount if collection_in_period else ZERO) - sum(
            (r.amount for r in p.refunds if in_range(r.created_at, start, end)), ZERO))
        if request.args.get('status') and row['status'] != request.args['status']:
            continue
        if request.args.get('channel') and row['channel'] != request.args['channel']:
            continue
        if request.args.get('method') and row['method'] != request.args['method']:
            continue
        if query not in ' '.join(str(row[k]) for k in ('reference', 'order_id', 'customer', 'email', 'method')).casefold():
            continue
        rows.append(row)
    sort = request.args.get('sort', 'date')
    if sort not in ('date', 'amount', 'customer', 'status', 'method', 'channel'):
        raise ValueError('Choose a supported transaction sort.')
    rows.sort(key=lambda r: r[sort], reverse=request.args.get('direction', 'desc') == 'desc')
    if request.path.endswith('/export'):
        columns = ['reference', 'order_id', 'customer', 'email', 'method', 'amount', 'status', 'date', 'channel', 'refunded', 'collection_in_period', 'refunds_in_period', 'net_collection_in_period', 'verification']
        output = io.StringIO(newline='')
        writer = csv.writer(output)
        writer.writerow(columns)
        for row in rows:
            values = [f"{row[k]:.2f}" if k in ('amount', 'refunded', 'collection_in_period', 'refunds_in_period', 'net_collection_in_period') else str(row[k]) for k in columns]
            writer.writerow(["'" + v if v.lstrip().startswith(('=', '+', '-', '@')) else v for v in values])
        return Response('\ufeff' + output.getvalue(), mimetype='text/csv', headers={
            'Content-Disposition': 'attachment; filename="audia-transactions.csv"'})
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError as error:
        raise ValueError('Choose a valid page number.') from error
    return jsonify(transactions=rows[(page-1)*20:page*20], count=len(rows), page=page,
                   pages=max(1, (len(rows)+19)//20), start=start.isoformat(), end=end.isoformat())


@commerce.get('/api/admin/transactions/<order_id>')
@require_user(admin=True)
def transaction_detail(order_id):
    order = db().get(Order, order_id)
    if not order:
        abort(404)
    return jsonify(transaction=transaction(order), order=order.public())


@commerce.post('/api/admin/transactions/<order_id>/refunds')
@require_user(admin=True)
def refund_payment(order_id):
    order = db().scalar(select(Order).where(Order.id == order_id).with_for_update())
    if not order:
        abort(404)
    item = refund(order, payload(), g.user)
    db().commit()
    return jsonify(refund_id=item.id, transaction=transaction(order), order=order.public())


@commerce.get('/receipts/<order_id>')
@require_page()
def receipt(order_id):
    order = db().get(Order, order_id)
    if not order or (g.user.role != 'admin' and order.user_id != g.user.id):
        abort(404)
    p = order.payment_record
    if not p or not p.receipt_number or not p.collected_at:
        abort(404)
    store = db().get(Setting, 'store_name')
    from audia.services.settings import settings
    from audia.services.reporting import MANILA
    from datetime import timezone
    stamp = p.collected_at.replace(tzinfo=timezone.utc) if p.collected_at.tzinfo is None else p.collected_at
    return render_template('shared/receipt.html', order=order, payment=p,
                           payer_number_masked=next((a.payer_number_masked for a in reversed(order.payment_attempts) if a.status in ('Succeeded','Verified') and a.payer_number_masked), ''),
                           receipt_footer=settings()['receipt_footer'],
                           qr_url=url_for('commerce.receipt_qr', receipt_number=p.receipt_number),
                           verification_url=url_for('commerce.verify_receipt', receipt_number=p.receipt_number),
                           store=store.value if store else 'AUDIA', paid_at=stamp.astimezone(MANILA).strftime('%b %d, %Y %I:%M %p Asia/Manila'),
                           refunded=p.amount if p.status == 'Refunded' and not p.refunds else sum((r.amount for r in p.refunds), 0))


def authorized_receipt(number):
    p = db().scalar(select(OrderPayment).where(OrderPayment.receipt_number == number))
    order = db().get(Order, p.order_id) if p and p.collected_at else None
    if not order or (g.user.role != 'admin' and order.user_id != g.user.id):
        abort(404)
    return order, p


@commerce.get('/verify/receipts/<receipt_number>')
@require_page()
def verify_receipt(receipt_number):
    order, payment = authorized_receipt(receipt_number)
    return render_template('shared/verification.html', order=order, payment=payment)


@commerce.get('/receipts/qr/<receipt_number>.svg')
@require_page()
def receipt_qr(receipt_number):
    authorized_receipt(receipt_number)
    import qrcode
    from qrcode.image.svg import SvgPathImage
    code = qrcode.make(url_for('commerce.verify_receipt', receipt_number=receipt_number, _external=True), image_factory=SvgPathImage, border=4)
    output = io.BytesIO()
    code.save(output)
    return Response(output.getvalue(), mimetype='image/svg+xml', headers={'Cache-Control':'private, no-store'})


@commerce.get('/refunds/<refund_id>')
@require_page()
def refund_confirmation(refund_id):
    item = db().get(Refund, refund_id)
    order = db().get(Order, item.payment_id) if item else None
    if not order or (g.user.role != 'admin' and order.user_id != g.user.id):
        abort(404)
    from audia.services.settings import settings
    request_item = db().scalar(select(RefundRequest).where(RefundRequest.refund_id == refund_id))
    return render_template('shared/refund_confirmation.html', order=order, refund=item, request_item=request_item,
                           store=settings()['store_name'])
