"""Catalog, guitar recommendations, saved instruments, and the support guide."""
import json
from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import select
from .auth import payload, require_user, string
from .database import db, seed_catalog
from .models import FinderProfile, Product, Wishlist, Setting

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


@catalog.get('/products')
@require_user()
def products():
    category = request.args.get('category', 'all').lower()
    query = request.args.get('q', '').lower()
    items = [p for p in products_data() if (category == 'all' or p['category'].lower() == category)
             and query in f'{p["name"]} {p["brand"]}'.lower()]
    return jsonify(products=items, count=len(items), preview='engine' not in current_app.extensions)


@catalog.get('/products/<int:product_id>')
@require_user()
def product(product_id):
    item = next((p for p in products_data() if p['id'] == product_id), None)
    return jsonify(item) if item else (jsonify(error='Product not found.'), 404)


@catalog.post('/finder')
@require_user()
def finder():
    data = payload()
    budget = data.get('budget', 20000)
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or not 1000 <= budget <= 500000:
        raise ValueError('Choose a budget between ₱1,000 and ₱500,000.')
    category = string(data, 'category', 30, 1)
    level = string(data, 'level', 30, 1)
    if category not in ('Electric', 'Acoustic', 'Bass', 'Classical') or level not in ('Beginner', 'Intermediate', 'Advanced'):
        raise ValueError('Choose a valid guitar type and experience level.')
    profile = dict(budget=budget, category=category, level=level, genre=string(data, 'genre', 40))
    def score(item):
        return ((50 if item['category'] == category else 0) + (25 if item['level'] == level else 0)
                + max(0, 25 - abs(item['price'] - budget) / budget * 25))
    items = [p for p in products_data() if p['stock'] > 0 and p['category'] in ('Electric', 'Acoustic', 'Bass', 'Classical')]
    ranked = sorted(items, key=score, reverse=True)[:2]
    if g.user:
        db().merge(FinderProfile(user_id=g.user.id, profile=json.dumps(profile)))
        db().commit()
    return jsonify(profile=profile, recommendations=ranked)


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


@catalog.post('/chat')
def chat():
    message = string(payload(), 'message', 1000, 1).lower()
    if 'beginner' in message:
        reply = 'For a beginner, prioritize comfort and a good setup. Try an entry-level electric for rock, or a steel-string acoustic for singer-songwriter music.'
    elif any(word in message for word in ('budget', '20k', '20,000')):
        reply = 'Use Guitar Finder to compare in-stock instruments within your budget. Leave room for a tuner, a case, and an amplifier if you choose electric.'
    elif 'acoustic' in message and 'electric' in message:
        reply = 'Choose acoustic for simplicity and an unplugged sound. Choose electric for effects, lighter strings, and rock tones; you will need an amplifier.'
    elif 'rock' in message:
        reply = 'For rock, look for an electric with humbuckers or a versatile pickup layout. Guitar Finder can match the catalog to your experience and budget.'
    elif any(word in message for word in ('order', 'delivery', 'return', 'warranty')):
        reply = 'Sign in and open My account to view your orders and delivery status. Contact the store for returns or warranty assistance.'
    else:
        reply = 'I am AUDI, your guitar shopping guide. I can help compare guitar types, budgets, experience levels, and accessories. What music would you like to play?'
    return jsonify(reply=reply)
