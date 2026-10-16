from flask import Flask, jsonify, request
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "saffron_smoke.db"

app = Flask(__name__)

MENU = [
    {"id": 1, "name": "Charred Paneer Tikka", "category": "Small plates", "price": 280, "rating": "4.9",
     "image": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=900&q=85",
     "description": "Smoky paneer, house spices, mint chutney and a squeeze of lime."},
    {"id": 2, "name": "Fire-Roasted Pizza", "category": "Mains", "price": 390, "rating": "4.8",
     "image": "https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?auto=format&fit=crop&w=900&q=85",
     "description": "Crisp edges, slow-roasted tomato, basil and creamy mozzarella."},
    {"id": 3, "name": "Saffron Butter Chicken", "category": "Mains", "price": 420, "rating": "5.0",
     "image": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=900&q=85",
     "description": "A rich, silky tomato gravy finished with cream and fragrant spices."},
    {"id": 4, "name": "Garden Burrata Salad", "category": "Small plates", "price": 310, "rating": "4.7",
     "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=85",
     "description": "Seasonal greens, juicy tomatoes, herbs and a bright citrus dressing."},
    {"id": 5, "name": "Truffle Mushroom Pasta", "category": "Mains", "price": 360, "rating": "4.9",
     "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=85",
     "description": "Silky pasta, golden mushrooms, parmesan and a hint of truffle."},
    {"id": 6, "name": "Chocolate Lava Cake", "category": "Desserts", "price": 240, "rating": "4.9",
     "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85",
     "description": "Warm chocolate cake with a molten centre and vanilla cream."},
    {"id": 7, "name": "Berry Cheesecake", "category": "Desserts", "price": 260, "rating": "4.8",
     "image": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=900&q=85",
     "description": "Creamy cheesecake, berry compote and a buttery biscuit base."},
    {"id": 8, "name": "Mango Mint Cooler", "category": "Drinks", "price": 150, "rating": "4.7",
     "image": "https://images.unsplash.com/photo-1513558161293-cd2a0e3e3c1c?auto=format&fit=crop&w=900&q=85",
     "description": "Ripe mango, fresh mint and sparkling citrus over ice."},
    {"id": 9, "name": "Cold Brew Tonic", "category": "Drinks", "price": 170, "rating": "4.8",
     "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=900&q=85",
     "description": "Slow-steeped coffee, bright citrus and a crisp tonic finish."}
]

def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS cart_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dish_id INTEGER NOT NULL,
                dish_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

@app.after_request
def add_cors_headers(response):
    # Demo only. For production, restrict this to your frontend origin.
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "saffron-smoke-backend"})

@app.route("/api/menu", methods=["GET"])
def menu():
    return jsonify({"items": MENU, "count": len(MENU)})

@app.route("/api/cart-events", methods=["POST", "OPTIONS"])
def cart_events():
    if request.method == "OPTIONS":
        return ("", 204)
    payload = request.get_json(silent=True) or {}
    try:
        dish_id = int(payload.get("dish_id", 0))
        quantity = int(payload.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "dish_id and quantity must be integers"}), 400

    dish = next((item for item in MENU if item["id"] == dish_id), None)
    if dish is None:
        return jsonify({"error": "Dish not found"}), 404
    if quantity < 1 or quantity > 20:
        return jsonify({"error": "quantity must be between 1 and 20"}), 400

    created_at = datetime.now(timezone.utc).isoformat()
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO cart_events (dish_id, dish_name, quantity, created_at) VALUES (?, ?, ?, ?)",
            (dish_id, dish["name"], quantity, created_at)
        )
        event_id = cursor.lastrowid

    return jsonify({
        "message": "Cart action saved",
        "event_id": event_id,
        "dish": dish["name"],
        "quantity": quantity,
        "created_at": created_at
    }), 201

@app.route("/api/cart-events", methods=["GET"])
def list_cart_events():
    # Useful for checking that frontend actions reached the backend in this learning demo.
    with get_db() as db:
        rows = db.execute(
            "SELECT id, dish_id, dish_name, quantity, created_at FROM cart_events ORDER BY id DESC LIMIT 100"
        ).fetchall()
    return jsonify({"events": [dict(row) for row in rows], "count": len(rows)})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)
