"""Product search/type filters and budget/skill Guitar Finder."""
import json
from flask import current_app, g, jsonify, request
from ..auth import payload, require_user, string
from ..database import db
from ..database.models import FinderProfile
from ..catalog.catalog import catalog, products_data


@catalog.get('/products')
@require_user()
def products():
    category = request.args.get('category', 'all').lower()
    query = request.args.get('q', '').lower()
    items = [p for p in products_data() if (category == 'all' or p['category'].lower() == category)
             and query in f'{p["name"]} {p["brand"]}'.lower()]
    return jsonify(products=items, count=len(items), preview='engine' not in current_app.extensions)


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


