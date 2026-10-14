"""Catalog products, availability, saved instruments, and store support."""
import json
from flask import Blueprint, current_app, g, jsonify
from sqlalchemy import select
from ..auth import require_user
from ..database import db, seed_catalog
from ..database.models import FinderProfile, Product, Wishlist, Setting

catalog = Blueprint('catalog', __name__, url_prefix='/api')


@catalog.get('/store')
def store_info():
    values = {'store_name': 'AUDIA Flagship', 'support_email': 'support@audia.ph'}
    if 'engine' in current_app.extensions:
        values.update({item.key: item.value for item in db().scalars(select(Setting))
                       if item.key in values})
    return jsonify(store=values)


def products_data():
    if 'engine' not in current_app.extensions:
        return seed_catalog(current_app)
    return [p.public() for p in db().scalars(select(Product).where(Product.active.is_(True)).order_by(Product.id))]


@catalog.get('/products/<int:product_id>')
@require_user()
def product(product_id):
    item = next((p for p in products_data() if p['id'] == product_id), None)
    return jsonify(item) if item else (jsonify(error='Product not found.'), 404)


@catalog.get('/account/saved')
@require_user()
def saved():
    items = db().scalars(select(Product).join(Wishlist).where(Wishlist.user_id == g.user.id, Product.active.is_(True)))
    profile = db().get(FinderProfile, g.user.id)
    return jsonify(products=[p.public() for p in items], profile=json.loads(profile.profile) if profile else None)


@catalog.put('/account/saved/<int:product_id>')
@require_user()
def save(product_id):
    product = db().get(Product, product_id)
    if not product or not product.active:
        return jsonify(error='This instrument is no longer available.'), 404
    # ON CONFLICT makes repeated save requests idempotent.
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    insert = pg_insert if db().bind.dialect.name == 'postgresql' else sqlite_insert
    db().execute(insert(Wishlist).values(user_id=g.user.id, product_id=product_id).on_conflict_do_nothing())
    db().commit()
    return jsonify(saved=True)


@catalog.delete('/account/saved/<int:product_id>')
@require_user()
def unsave(product_id):
    record = db().get(Wishlist, (g.user.id, product_id))
    if record:
        db().delete(record)
        db().commit()
    return jsonify(saved=False)

