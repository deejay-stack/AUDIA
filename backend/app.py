from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "templates"),
    static_folder=str(PROJECT_ROOT / "static"),
)
CORS(app)


@app.get("/")
def storefront():
    return render_template("index.html")

PRODUCTS = [
    {"id": 1, "name": "Squier Sonic Stratocaster", "brand": "Fender", "category": "Electric", "price": 12990, "rating": 4.8, "reviews": 124, "color": "Arctic White", "level": "Beginner", "stock": 8, "badge": "Bestseller", "image": "https://images.unsplash.com/photo-1550291652-6ea9114a47b1?auto=format&fit=crop&w=1100&q=85", "description": "Bright, versatile tone with a slim neck that feels effortless from the first chord.", "specs": ["Poplar body", "Ceramic pickups", "21-fret maple neck"]},
    {"id": 2, "name": "Epiphone Les Paul Studio", "brand": "Epiphone", "category": "Electric", "price": 28990, "rating": 4.9, "reviews": 89, "color": "Ebony", "level": "Intermediate", "stock": 4, "badge": "Staff pick", "image": "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=1100&q=85", "description": "Rich sustain and muscular humbucker tone made for rock, blues, and soaring leads.", "specs": ["Mahogany body", "Dual humbuckers", "22 medium-jumbo frets"]},
    {"id": 3, "name": "Yamaha FG800 Natural", "brand": "Yamaha", "category": "Acoustic", "price": 15490, "rating": 4.7, "reviews": 206, "color": "Natural", "level": "Beginner", "stock": 11, "badge": "Top rated", "image": "https://images.unsplash.com/photo-1525201548942-d8732f6617a0?auto=format&fit=crop&w=1100&q=85", "description": "A solid-top acoustic with balanced projection and dependable playability for everyday music.", "specs": ["Solid spruce top", "Nato back & sides", "Scalloped bracing"]},
    {"id": 4, "name": "Ibanez GSR200 Bass", "brand": "Ibanez", "category": "Bass", "price": 18490, "rating": 4.6, "reviews": 67, "color": "Black", "level": "Beginner", "stock": 6, "badge": "Great value", "image": "https://images.unsplash.com/photo-1550985616-10810253b84d?auto=format&fit=crop&w=1100&q=85", "description": "Fast neck, focused low end, and active tone shaping in a lightweight stage-ready bass.", "specs": ["Poplar body", "Active EQ", "22 medium frets"]},
    {"id": 5, "name": "Cordoba C5 Classical", "brand": "Cordoba", "category": "Classical", "price": 24990, "rating": 4.8, "reviews": 51, "color": "Natural", "level": "Intermediate", "stock": 3, "badge": "Artisan", "image": "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=1100&q=85", "description": "Warm nylon-string character, traditional fan bracing, and a comfortable hand-finished neck.", "specs": ["Solid cedar top", "Mahogany back & sides", "Savarez strings"]},
    {"id": 6, "name": "PRS SE Custom 24", "brand": "PRS", "category": "Electric", "price": 53990, "rating": 4.9, "reviews": 43, "color": "Charcoal Burst", "level": "Advanced", "stock": 2, "badge": "Premium", "image": "https://images.unsplash.com/photo-1605020420620-20c943cc4669?auto=format&fit=crop&w=1100&q=85", "description": "Polished playability and articulate coil-split tones for players who need one guitar to do it all.", "specs": ["Maple top", "85/15 S pickups", "24 frets"]},
]

SALES = [
    {"id": "AUD-30128", "customer": "Mika Santos", "email": "mika@example.com", "product": "Squier Sonic Stratocaster", "date": "Sep 7, 2026", "amount": 12990, "payment": "GCash", "status": "Paid"},
    {"id": "AUD-30127", "customer": "Paolo Reyes", "email": "paolo@example.com", "product": "Yamaha FG800 Natural", "date": "Sep 7, 2026", "amount": 15490, "payment": "Visa •• 2048", "status": "Paid"},
    {"id": "AUD-30126", "customer": "Anna Lim", "email": "anna@example.com", "product": "Complete Starter Rig", "date": "Sep 6, 2026", "amount": 19990, "payment": "Maya", "status": "Processing"},
    {"id": "AUD-30125", "customer": "Rafael Cruz", "email": "rafael@example.com", "product": "Epiphone Les Paul Studio", "date": "Sep 6, 2026", "amount": 28990, "payment": "Mastercard •• 8173", "status": "Paid"},
    {"id": "AUD-30124", "customer": "Bea Torres", "email": "bea@example.com", "product": "Ibanez GSR200 Bass", "date": "Sep 5, 2026", "amount": 18490, "payment": "COD", "status": "Pending"},
    {"id": "AUD-30123", "customer": "Kyle Mendoza", "email": "kyle@example.com", "product": "Cordoba C5 Classical", "date": "Sep 5, 2026", "amount": 24990, "payment": "GCash", "status": "Refunded"},
]


@app.get("/api/health")
def health():
    return jsonify(status="ok", service="AUDIA API")


@app.get("/api/products")
def products():
    category = request.args.get("category")
    query = request.args.get("q", "").lower()
    results = PRODUCTS
    if category and category.lower() != "all":
        results = [p for p in results if p["category"].lower() == category.lower()]
    if query:
        results = [p for p in results if query in f'{p["name"]} {p["brand"]}'.lower()]
    return jsonify(products=results, count=len(results))


@app.get("/api/products/<int:product_id>")
def product(product_id):
    match = next((p for p in PRODUCTS if p["id"] == product_id), None)
    return (jsonify(match), 200) if match else (jsonify(error="Product not found"), 404)


@app.post("/api/finder")
def finder():
    profile = request.get_json(silent=True) or {}
    budget = int(profile.get("budget", 20000))
    category = profile.get("category", "Electric")
    level = profile.get("level", "Beginner")

    def score(item):
        points = 0
        if item["category"].lower() == category.lower():
            points += 50
        if item["level"].lower() == level.lower():
            points += 25
        points += max(0, 25 - abs(item["price"] - budget) / max(budget, 1) * 25)
        return points

    ranked = sorted(PRODUCTS, key=score, reverse=True)[:2]
    return jsonify(profile=profile, recommendations=ranked)


@app.post("/api/auth/login")
def login():
    credentials = request.get_json(silent=True) or {}
    email = credentials.get("email", "").strip().lower()
    password = credentials.get("password", "")
    role = credentials.get("role", "customer")

    if role == "admin":
        if email != "admin@audia.ph" or password != "admin123":
            return jsonify(error="Incorrect administrator credentials"), 401
        user = {"name": "AUDIA Admin", "email": email, "role": "admin"}
    else:
        if "@" not in email or len(password) < 6:
            return jsonify(error="Incorrect customer credentials"), 401
        user = {"name": "AUDIA Member", "email": email, "role": "customer"}

    return jsonify(user=user, token=f"audia-demo-{role}-token")


@app.get("/api/admin/sales")
def admin_sales():
    return jsonify(sales=SALES, count=len(SALES))


@app.get("/api/admin/summary")
def admin_summary():
    return jsonify(
        gross_revenue=486820,
        total_orders=148,
        new_customers=39,
        low_stock_items=sum(1 for product in PRODUCTS if product["stock"] <= 4),
    )


@app.post("/api/chat")
def chat():
    message = (request.get_json(silent=True) or {}).get("message", "").lower()
    if "beginner" in message:
        reply = "For a beginner, prioritize comfort and a good setup. The Squier Sonic Stratocaster is a friendly electric choice, while the Yamaha FG800 is excellent if you prefer acoustic."
    elif "20k" in message or "20,000" in message or "budget" in message:
        reply = "Under ₱20,000, my strongest picks are the Squier Sonic Stratocaster for electric, Yamaha FG800 for acoustic, and Ibanez GSR200 if bass is calling you."
    elif "acoustic" in message and "electric" in message:
        reply = "Choose acoustic if you want simplicity and singer-songwriter sounds. Choose electric if you love rock, effects, easier strings, and don't mind using an amp."
    elif "rock" in message:
        reply = "For rock, look for an electric with humbuckers or a versatile pickup layout. The Epiphone Les Paul Studio gives thick, powerful tone; the Squier is brighter and more flexible."
    else:
        reply = "I can help with guitar types, budget, tone, skill level, accessories, or comparing models. What kind of music do you want to play?"
    return jsonify(reply=reply)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
