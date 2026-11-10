"""Integrated request review, delivery, secure uploads and customer operations."""
import io
import json
import math
import secrets
import warnings
from pathlib import Path

from flask import Blueprint, abort, current_app, g, jsonify, request, send_file
from sqlalchemy import select, delete
from audia.database import db
from audia.database.models import (Order, RefundRequest, Delivery, OrderEvent, Upload, Product,
                                   InventoryMovement, User, AccountStatus, LoginSession, Notification,
                                   AdminAudit, RequestEvent, utc_iso, now)
from audia.routes.auth import require_user, payload, string
from audia.services.returns import request_refund, review_request, request_public, requests_for

operations = Blueprint('operations', __name__)


def locked_order(identifier, customer=False):
    query = select(Order).where(Order.id == identifier.upper())
    if customer:
        query = query.where(Order.user_id == g.user.id)
    item = db().scalar(query.with_for_update())
    if not item:
        abort(404)
    return item


@operations.get('/api/orders/<order_id>/requests')
@require_user()
def customer_requests(order_id):
    order = locked_order(order_id, customer=g.user.role != 'admin')
    return jsonify(requests=[request_public(r) for r in requests_for(order)])


@operations.post('/api/orders/<order_id>/requests')
@require_user(role='customer')
def new_request(order_id):
    order = locked_order(order_id, customer=True)
    item = request_refund(order, payload(), g.user)
    db().commit()
    return jsonify(request=request_public(item)), 201


@operations.post('/api/orders/<order_id>/requests/<request_id>/reply')
@require_user(role='customer')
def request_reply(order_id, request_id):
    order = locked_order(order_id, customer=True)
    item = next((r for r in requests_for(order) if r.id == request_id), None)
    if not item:
        abort(404)
    if item.status not in ('Requested', 'Under Review'):
        raise ValueError('This request is no longer accepting additional information.')
    note = string(payload(), 'note', 300, 3)
    item.events.append(RequestEvent(status=item.status, note='Customer: ' + note[:290], actor_id=g.user.id))
    db().commit()
    return jsonify(request=request_public(item))


@operations.get('/api/account/notifications')
@require_user(role='customer')
def notifications():
    rows = list(db().scalars(select(Notification).where(Notification.user_id == g.user.id).order_by(Notification.id.desc()).limit(30)))
    return jsonify(notifications=[dict(id=n.id,order_id=n.order_id,message=n.message,read=n.read,at=utc_iso(n.created_at)) for n in rows])


@operations.post('/api/account/notifications/read')
@require_user(role='customer')
def read_notifications():
    from sqlalchemy import update
    db().execute(update(Notification).where(Notification.user_id == g.user.id, Notification.read.is_(False)).values(read=True))
    db().commit()
    return jsonify(message='Notifications marked as read.')


@operations.get('/api/admin/requests')
@require_user(admin=True)
def request_list():
    query = select(RefundRequest).order_by(RefundRequest.created_at.desc())
    if request.args.get('status'):
        query = query.where(RefundRequest.status == request.args['status'])
    rows = []
    search = request.args.get('q', '').casefold()
    for item in db().scalars(query):
        order = db().get(Order, item.order_id)
        if search in f'{item.id} {order.id} {order.customer} {item.reason}'.casefold():
            rows.append(dict(request_public(item), customer=order.customer))
    page = max(1, int(request.args.get('page', 1)))
    if request.args.get('sort') == 'amount':
        rows.sort(key=lambda r:r['amount'], reverse=True)
    return jsonify(requests=rows[(page-1)*20:page*20], count=len(rows), page=page, pages=max(1,(len(rows)+19)//20))


@operations.patch('/api/admin/requests/<request_id>')
@require_user(admin=True)
def review(request_id):
    # All refund paths lock order first to serialize request, direct refund and cancellation.
    identifier = db().scalar(select(RefundRequest.order_id).where(RefundRequest.id == request_id))
    if not identifier:
        abort(404)
    order = locked_order(identifier)
    item = next(r for r in requests_for(order) if r.id == request_id)
    review_request(order, item, payload(), g.user)
    db().commit()
    return jsonify(request=request_public(item), order=order.public())


@operations.post('/api/admin/payments/<order_id>/verify')
@require_user(admin=True)
def verify_payment(order_id):
    from audia.services.payments import verify_bank
    order = locked_order(order_id)
    verify_bank(order, payload(), g.user)
    db().commit()
    return jsonify(order=order.public())


def delivery_data(order):
    item = db().get(Delivery, order.id)
    from audia.services.settings import settings
    config = settings()
    return dict(delivery=item.public() if item else None, address=order.address, status=order.status,
                map_provider=config['map_provider'], google_maps_key=config['google_maps_key'],
                map_tile_url=config['map_tile_url'])


@operations.get('/api/orders/<order_id>/delivery')
@require_user()
def delivery(order_id):
    order = db().get(Order, order_id.upper())
    if not order or (g.user.role != 'admin' and order.user_id != g.user.id):
        abort(404)
    return jsonify(**delivery_data(order))


@operations.put('/api/admin/orders/<order_id>/delivery')
@require_user(admin=True)
def update_delivery(order_id):
    order = locked_order(order_id)
    data = payload()
    if order.status in ('Cancelled','Rejected','Refunded','Returned'):
        raise ValueError('Delivery cannot be updated for this order state.')
    route = data.get('route', [])
    if not isinstance(route, list) or not 2 <= len(route) <= 30:
        raise ValueError('Supply 2–30 simulated route points, from dispatch to destination.')
    for point in route:
        if not isinstance(point, list) or len(point) != 2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in point) or not (-90 <= point[0] <= 90 and -180 <= point[1] <= 180):
            raise ValueError('Each route point must contain valid latitude and longitude.')
    progress = data.get('progress', 0)
    if type(progress) is not int or not 0 <= progress < len(route):
        raise ValueError('Progress must identify a point in the configured route (starting at 0).')
    item = db().get(Delivery, order.id) or Delivery(order_id=order.id)
    item.method = string(data, 'method', 100, 2)
    item.reference = string(data, 'reference', 100) or 'SIM-' + order.id
    item.window = string(data, 'window', 150)
    item.note = string(data, 'note', 250, 3)
    item.route_json, item.progress = json.dumps(route), progress
    if data.get('status') and data['status'] != order.status:
        from audia.services.orders import update_order
        update_order(order, {'status':data['status'], 'expected_status':data.get('expected_status', order.status)}, g.user)
    db().add(item)
    order.events.append(OrderEvent(status=order.status, kind='delivery', actor_id=g.user.id,
                        note=f'Simulated delivery point {progress+1}/{len(route)}: {item.note}'[:300]))
    from audia.services.notifications import notify
    notify(order, 'Delivery update: ' + item.note)
    db().commit()
    return jsonify(**delivery_data(order))


@operations.post('/api/uploads')
@require_user()
def upload_image():
    """Decode/re-encode raster images; random filenames, no SVG, no original metadata."""
    from PIL import Image, UnidentifiedImageError
    purpose = request.form.get('purpose')
    if purpose not in ('evidence','product') or (purpose == 'product' and g.user.role != 'admin'):
        abort(403)
    file = request.files.get('image')
    if not file:
        raise ValueError('Choose a PNG, JPEG or WebP image.')
    raw = file.stream.read(4*1024*1024+1)
    if len(raw) > 4*1024*1024:
        raise ValueError('Images must be at most 4 MB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as source:
                if source.format not in ('PNG','JPEG','WEBP') or source.width*source.height > 16000000:
                    raise ValueError('Choose a raster image no larger than 16 megapixels.')
                source.load()
                image = source.convert('RGB')
                image.thumbnail((1600,1600))
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise ValueError('That file is not a supported image.') from error
    item = Upload(id=secrets.token_hex(16), user_id=g.user.id, purpose=purpose)
    folder = Path(current_app.instance_path)/'uploads'
    folder.mkdir(parents=True, exist_ok=True)
    target = folder/(item.id+'.jpg')
    image.save(target, 'JPEG', quality=85)
    db().add(item)
    try:
        db().commit()
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return jsonify(id=item.id, url='/uploads/'+item.id), 201


@operations.get('/uploads/<identifier>')
def uploaded_image(identifier):
    item = db().get(Upload, identifier)
    if not item:
        abort(404)
    if item.purpose != 'product' and (not g.user or (g.user.role != 'admin' and item.user_id != g.user.id)):
        abort(404)
    response = send_file(Path(current_app.instance_path)/'uploads'/(item.id+'.jpg'), mimetype='image/jpeg')
    if item.purpose == 'evidence':
        response.headers['Cache-Control'] = 'private, no-store'
    return response


@operations.get('/api/admin/inventory/movements')
@require_user(admin=True)
def movements():
    query = select(InventoryMovement).order_by(InventoryMovement.id.desc())
    if request.args.get('product_id'):
        query = query.where(InventoryMovement.product_id == int(request.args['product_id']))
    page = max(1, int(request.args.get('page', 1)))
    rows = list(db().scalars(query))
    if request.args.get('q'):
        q = request.args['q'].casefold()
        rows = [r for r in rows if q in f'{r.product_id} {r.order_id or ""} {r.reason}'.casefold()]
    return jsonify(movements=[r.public() for r in rows[(page-1)*20:page*20]], count=len(rows), page=page, pages=max(1,(len(rows)+19)//20))


@operations.get('/api/admin/audit')
@require_user(admin=True)
def admin_audit():
    return jsonify(events=[dict(actor_id=e.actor_id, action=e.action, at=utc_iso(e.created_at)) for e in
                   db().scalars(select(AdminAudit).order_by(AdminAudit.id.desc()).limit(30))])


@operations.get('/api/admin/products/<int:identifier>/history')
@require_user(admin=True)
def product_history(identifier):
    from audia.database.models import OrderItem
    product = db().get(Product, identifier)
    if not product:
        abort(404)
    identifiers = select(OrderItem.order_id).where(OrderItem.product_id == identifier)
    orders = list(db().scalars(select(Order).where(Order.id.in_(identifiers)).order_by(Order.created_at.desc())))
    return jsonify(product=product.public(), orders=[o.public() for o in orders])


@operations.get('/api/admin/customers/<int:identifier>')
@require_user(admin=True)
def customer_detail(identifier):
    user = db().get(User, identifier)
    if not user or user.role != 'customer':
        abort(404)
    orders = list(db().scalars(select(Order).where(Order.user_id == identifier).order_by(Order.created_at.desc())))
    status = db().get(AccountStatus, identifier)
    return jsonify(customer=user.public(), suspended=bool(status and status.suspended),
                   reason=status.reason if status else '', orders=[o.public() for o in orders],
                   requests=[request_public(r) for o in orders for r in requests_for(o)])


@operations.put('/api/admin/customers/<int:identifier>/status')
@require_user(admin=True)
def customer_status(identifier):
    user = db().scalar(select(User).where(User.id == identifier).with_for_update())
    if not user or user.role != 'customer':
        abort(404)
    data = payload()
    if type(data.get('suspended')) is not bool:
        raise ValueError('Choose a valid account status.')
    note = string(data, 'reason', 200, 3)
    db().merge(AccountStatus(user_id=identifier, suspended=data['suspended'], reason=note, actor_id=g.user.id, updated_at=now()))
    if data['suspended']:
        db().execute(delete(LoginSession).where(LoginSession.user_id == identifier))
    db().add(AdminAudit(actor_id=g.user.id, action=f'Customer #{identifier} access {"suspended" if data["suspended"] else "restored"}: {note}'[:300]))
    db().commit()
    return jsonify(message='Customer account status updated.')
