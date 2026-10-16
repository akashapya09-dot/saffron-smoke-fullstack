from flask import Flask, jsonify, request, Response
from pathlib import Path
from datetime import datetime, timezone, date
import sqlite3, re, secrets

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "saffron_smoke.db"
app = Flask(__name__)

MENU = [
 {"id":1,"name":"Charred Paneer Tikka","category":"Small plates","price":280,"rating":"4.9","image":"https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=900&q=85","description":"Smoky paneer, house spices, mint chutney and a squeeze of lime."},
 {"id":2,"name":"Fire-Roasted Pizza","category":"Mains","price":390,"rating":"4.8","image":"https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?auto=format&fit=crop&w=900&q=85","description":"Crisp edges, slow-roasted tomato, basil and creamy mozzarella."},
 {"id":3,"name":"Saffron Butter Chicken","category":"Mains","price":420,"rating":"5.0","image":"https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=900&q=85","description":"A rich, silky tomato gravy finished with cream and fragrant spices."},
 {"id":4,"name":"Garden Burrata Salad","category":"Small plates","price":310,"rating":"4.7","image":"https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=85","description":"Seasonal greens, juicy tomatoes, herbs and a bright citrus dressing."},
 {"id":5,"name":"Truffle Mushroom Pasta","category":"Mains","price":360,"rating":"4.9","image":"https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=85","description":"Silky pasta, golden mushrooms, parmesan and a hint of truffle."},
 {"id":6,"name":"Chocolate Lava Cake","category":"Desserts","price":240,"rating":"4.9","image":"https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85","description":"Warm chocolate cake with a molten centre and vanilla cream."},
 {"id":7,"name":"Berry Cheesecake","category":"Desserts","price":260,"rating":"4.8","image":"https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=900&q=85","description":"Creamy cheesecake, berry compote and a buttery biscuit base."},
 {"id":8,"name":"Mango Mint Cooler","category":"Drinks","price":150,"rating":"4.7","image":"https://images.unsplash.com/photo-1513558161293-cd2a0e3e3c1c?auto=format&fit=crop&w=900&q=85","description":"Ripe mango, fresh mint and sparkling citrus over ice."},
 {"id":9,"name":"Cold Brew Tonic","category":"Drinks","price":170,"rating":"4.8","image":"https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=900&q=85","description":"Slow-steeped coffee, bright citrus and a crisp tonic finish."}
]

def get_db():
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute("CREATE TABLE IF NOT EXISTS cart_events (id INTEGER PRIMARY KEY AUTOINCREMENT,dish_id INTEGER NOT NULL,dish_name TEXT NOT NULL,quantity INTEGER NOT NULL,created_at TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS reservations (id INTEGER PRIMARY KEY AUTOINCREMENT,reference TEXT NOT NULL UNIQUE,name TEXT NOT NULL,email TEXT NOT NULL,phone TEXT NOT NULL,guests INTEGER NOT NULL,reservation_date TEXT NOT NULL,reservation_time TEXT NOT NULL,notes TEXT NOT NULL DEFAULT '',status TEXT NOT NULL DEFAULT 'requested',created_at TEXT NOT NULL)")

@app.after_request
def cors(response):
    # Demo deployment: restrict this to your frontend origin for production.
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.route('/api/health')
def health():
    return jsonify({'status':'ok','service':'saffron-smoke-backend'})

@app.route('/api/menu')
def menu():
    return jsonify({'items':MENU,'count':len(MENU)})

@app.route('/api/cart-events', methods=['GET','POST','OPTIONS'])
def cart_events():
    if request.method == 'OPTIONS': return ('',204)
    if request.method == 'GET':
        with get_db() as db:
            rows=db.execute('SELECT id,dish_id,dish_name,quantity,created_at FROM cart_events ORDER BY id DESC LIMIT 100').fetchall()
        return jsonify({'events':[dict(x) for x in rows],'count':len(rows)})
    data=request.get_json(silent=True) or {}
    try: dish_id=int(data.get('dish_id',0)); quantity=int(data.get('quantity',1))
    except (TypeError,ValueError): return jsonify({'error':'dish_id and quantity must be integers'}),400
    dish=next((x for x in MENU if x['id']==dish_id),None)
    if not dish: return jsonify({'error':'Dish not found'}),404
    if not 1 <= quantity <= 20: return jsonify({'error':'quantity must be between 1 and 20'}),400
    created=datetime.now(timezone.utc).isoformat()
    with get_db() as db:
        cur=db.execute('INSERT INTO cart_events(dish_id,dish_name,quantity,created_at) VALUES(?,?,?,?)',(dish_id,dish['name'],quantity,created))
    return jsonify({'message':'Cart action saved','event_id':cur.lastrowid,'dish':dish['name'],'quantity':quantity,'created_at':created}),201

@app.route('/api/reservations', methods=['POST','OPTIONS'])
def create_reservation():
    if request.method == 'OPTIONS': return ('',204)
    data=request.get_json(silent=True) or {}
    name=str(data.get('name','')).strip(); email=str(data.get('email','')).strip().lower(); phone=str(data.get('phone','')).strip()
    notes=str(data.get('notes','')).strip(); res_date=str(data.get('date','')).strip(); res_time=str(data.get('time','')).strip()
    try: guests=int(data.get('guests',0))
    except (ValueError,TypeError): return jsonify({'error':'Guests must be a number.'}),400
    if len(name)<2 or len(name)>100: return jsonify({'error':'Enter a name between 2 and 100 characters.'}),400
    if len(email)>160 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email): return jsonify({'error':'Enter a valid email address.'}),400
    if len(phone)<7 or len(phone)>20 or not re.fullmatch(r'[+()\d\s.-]{7,20}',phone): return jsonify({'error':'Enter a valid phone number.'}),400
    if not 1 <= guests <= 12: return jsonify({'error':'Reservations are available for 1 to 12 guests online.'}),400
    if len(notes)>500: return jsonify({'error':'Special requests must be 500 characters or fewer.'}),400
    try:
        chosen_date=date.fromisoformat(res_date)
        chosen_time=datetime.strptime(res_time,'%H:%M').time()
    except ValueError: return jsonify({'error':'Choose a valid date and time.'}),400
    if chosen_date <= date.today(): return jsonify({'error':'Please choose a future date.'}),400
    if chosen_time.hour < 11 or chosen_time.hour > 22 or (chosen_time.hour == 22 and chosen_time.minute != 0) or chosen_time.minute not in (0,30):
        return jsonify({'error':'Reservations are available from 11:00 to 22:00, on the hour or half-hour.'}),400
    reference='SS-'+secrets.token_hex(3).upper()
    created=datetime.now(timezone.utc).isoformat()
    try:
        with get_db() as db:
            db.execute('INSERT INTO reservations(reference,name,email,phone,guests,reservation_date,reservation_time,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(reference,name,email,phone,guests,res_date,res_time,notes,created))
    except sqlite3.Error:
        app.logger.exception('Could not save reservation')
        return jsonify({'error':'We could not save your reservation right now. Please try again.'}),500
    return jsonify({'message':'Reservation request saved. This is a request, not a confirmed table assignment.','reference':reference,'reservation':{'name':name,'date':res_date,'time':res_time,'guests':guests,'status':'requested'}}),201

@app.route('/api/reservations/availability')
def reservation_availability():
    res_date=request.args.get('date','').strip()
    try:
        if date.fromisoformat(res_date) <= date.today(): raise ValueError()
    except ValueError: return jsonify({'error':'Provide a future date in YYYY-MM-DD format.'}),400
    with get_db() as db:
        rows=db.execute("SELECT reservation_time,COUNT(*) AS requests FROM reservations WHERE reservation_date=? AND status='requested' GROUP BY reservation_time ORDER BY reservation_time",(res_date,)).fetchall()
    return jsonify({'date':res_date,'requests_by_time':[dict(r) for r in rows],'note':'Request counts only; staff must confirm actual table availability.'})

OPENAPI = {
 "openapi":"3.0.3",
 "info":{"title":"Saffron & Smoke API","version":"1.0.0","description":"Restaurant menu, demo cart events, and table reservation requests."},
 "servers":[{"url":"/","description":"Current backend server"}],
 "paths":{
  "/api/health":{"get":{"summary":"Health check","responses":{"200":{"description":"Backend is running"}}}},
  "/api/menu":{"get":{"summary":"List menu items","responses":{"200":{"description":"Menu items and count"}}}},
  "/api/cart-events":{"get":{"summary":"List recent demo cart events","responses":{"200":{"description":"Recent cart events"}}},"post":{"summary":"Record an add-to-order event","requestBody":{"required":True,"content":{"application/json":{"schema":{"type":"object","required":["dish_id"],"properties":{"dish_id":{"type":"integer","example":1},"quantity":{"type":"integer","minimum":1,"maximum":20,"default":1}}}}}},"responses":{"201":{"description":"Cart action recorded"},"400":{"description":"Invalid payload"},"404":{"description":"Dish not found"}}}},
  "/api/reservations":{"post":{"summary":"Request a restaurant reservation","description":"Saves a request in SQLite. This is not a confirmed table assignment.","requestBody":{"required":True,"content":{"application/json":{"schema":{"type":"object","required":["name","email","phone","guests","date","time"],"properties":{"name":{"type":"string","example":"Asha Rao"},"email":{"type":"string","format":"email","example":"asha@example.com"},"phone":{"type":"string","example":"+91 98765 43210"},"guests":{"type":"integer","minimum":1,"maximum":12,"example":2},"date":{"type":"string","format":"date","example":"2027-01-15"},"time":{"type":"string","example":"19:00"},"notes":{"type":"string","maxLength":500}}}}}},"responses":{"201":{"description":"Reservation request saved with reference"},"400":{"description":"Validation error"},"500":{"description":"Could not save request"}}}},
  "/api/reservations/availability":{"get":{"summary":"View request counts for a date (not guaranteed availability)","parameters":[{"name":"date","in":"query","required":True,"schema":{"type":"string","format":"date"},"example":"2027-01-15"}],"responses":{"200":{"description":"Request counts for the date"},"400":{"description":"Invalid date"}}}}
 }
}

@app.route('/openapi.json')
def openapi(): return jsonify(OPENAPI)

@app.route('/docs')
@app.route('/docs/')
def docs():
    page="<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Saffron & Smoke API Docs</title><link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@5/swagger-ui.css'></head><body><div id='swagger-ui'></div><script src='https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js'></script><script>window.onload=()=>SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui',deepLinking:true});</script></body></html>"
    return Response(page,mimetype='text/html')

init_db()
if __name__=='__main__':
    app.run(host='0.0.0.0',port=8000)
