from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import datetime, os

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "replace_this_with_a_strong_random_value"

# === EMBEDDED CONFIG ===
MONGO_URI = "mongodb+srv://jubilantlandhotelloungebarspa_db_user:Juba73812@@@jubilanthotel.dybd1xl.mongodb.net/jubilant_hotel?retryWrites=true&w=majority"
ADMINS = {
    "jubilantlandhotelloungebarspa@gmail.com": "Juba73812@@@",
    "yinkakanbi73812@gmail.com": "Juba73812@@@"
}
ROOM_PRICES = {"Diamond": 20000, "Gold": 40000}
PAYMENT_INFO = {"method": "Moniepoint", "account": "9160569980", "name": "Olayinka AKANBI"}
# =======================

app.config["MONGO_URI"] = MONGO_URI
mongo = PyMongo(app)
db = mongo.db

def fmt_dt(dt):
    if isinstance(dt, datetime.datetime):
        return dt.strftime("%B %d, %Y")
    return str(dt)

# Home - renders templates/index.html (uses your static css/js)
@app.route("/")
def home():
    try:
        approved = list(db.reviews.find({"approved": True}).sort("created_at", -1))
        reviews = [{"_id": str(r["_id"]), "name": r.get("name",""), "comment": r.get("comment",""), "created_at": fmt_dt(r.get("created_at"))} for r in approved]
    except Exception:
        reviews = []
    settings = db.settings.find_one({"key":"meta"}) or {}
    room_prices = settings.get("roomPrices", ROOM_PRICES)
    payment = settings.get("payment", PAYMENT_INFO)
    return render_template("index.html", reviews=reviews, room_prices=room_prices, payment=payment)

# Bookings
@app.route("/book", methods=["POST"])
def book():
    data = request.form or request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    room = data.get("room") or data.get("room_type")
    checkin = data.get("checkin")
    checkout = data.get("checkout")
    if not (name and email and room and checkin and checkout):
        flash("Missing required booking fields","error")
        return redirect(url_for("home"))
    settings = db.settings.find_one({"key":"meta"}) or {}
    price = settings.get("roomPrices", ROOM_PRICES).get(room, ROOM_PRICES.get(room, ROOM_PRICES["Diamond"]))
    booking = {"name":name,"email":email,"phone":phone,"room":room,"price":int(price),"checkin":checkin,"checkout":checkout,"approved":False,"created_at":datetime.datetime.utcnow()}
    db.bookings.insert_one(booking)
    flash("Booking submitted. Please send payment to the account shown and notify admin.","success")
    return redirect(url_for("home"))

# Reviews
@app.route("/review", methods=["POST"])
def review():
    data = request.form or request.get_json(silent=True) or {}
    name = data.get("name"); email = data.get("email"); comment = data.get("comment") or data.get("experience")
    if not (name and email and comment):
        flash("Missing required review fields","error"); return redirect(url_for("home"))
    review = {"name":name,"email":email,"comment":comment,"approved":False,"created_at":datetime.datetime.utcnow()}
    db.reviews.insert_one(review)
    flash("Review submitted — it will appear after admin approval.","success")
    return redirect(url_for("home"))

# API to fetch approved reviews (AJAX)
@app.route("/api/reviews", methods=["GET"])
def api_reviews():
    try:
        approved = list(db.reviews.find({"approved":True}).sort("created_at", -1))
        out = [{"_id":str(r["_id"]), "name":r.get("name",""), "comment":r.get("comment",""), "created_at": fmt_dt(r.get("created_at"))} for r in approved]
        return jsonify(out)
    except Exception as e:
        return jsonify([])

# Admin auth + dashboard
@app.route("/admin", methods=["GET","POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("email") or request.form.get("username")
        password = request.form.get("password")
        if username in ADMINS and ADMINS[username] == password:
            session["admin_user"] = username; return redirect(url_for("admin_dashboard"))
        rec = db.admins.find_one({"email":username,"password":password})
        if rec:
            session["admin_user"] = username; return redirect(url_for("admin_dashboard"))
        error = "Invalid credentials"
    return render_template("admin_login.html", error=error)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_user", None); return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_user" not in session: return redirect(url_for("admin_login"))
    pending_reviews = list(db.reviews.find({"approved":False}).sort("created_at",-1))
    bookings = list(db.bookings.find().sort("created_at",-1))
    settings = db.settings.find_one({"key":"meta"}) or {}
    room_prices = settings.get("roomPrices", ROOM_PRICES); payment = settings.get("payment", PAYMENT_INFO)
    return render_template("admin_dashboard.html", pending_reviews=pending_reviews, bookings=bookings, room_prices=room_prices, payment=payment)

@app.route("/admin/approve_review/<rid>", methods=["POST"])
def admin_approve_review(rid):
    if "admin_user" not in session: return jsonify({"error":"unauthorized"}),403
    try: db.reviews.update_one({"_id":ObjectId(rid)}, {"$set":{"approved":True}})
    except: pass
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete_review/<rid>", methods=["POST"])
def admin_delete_review(rid):
    if "admin_user" not in session: return jsonify({"error":"unauthorized"}),403
    try: db.reviews.delete_one({"_id":ObjectId(rid)})
    except: pass
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/approve_booking/<bid>", methods=["POST"])
def admin_approve_booking(bid):
    if "admin_user" not in session: return jsonify({"error":"unauthorized"}),403
    try: db.bookings.update_one({"_id":ObjectId(bid)}, {"$set":{"approved":True}})
    except: pass
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/update_prices", methods=["POST"])
def admin_update_prices():
    if "admin_user" not in session: return jsonify({"error":"unauthorized"}),403
    try:
        diamond = int(request.form.get("diamond") or ROOM_PRICES["Diamond"])
        gold = int(request.form.get("gold") or ROOM_PRICES["Gold"])
    except: diamond = ROOM_PRICES["Diamond"]; gold = ROOM_PRICES["Gold"]
    meta = db.settings.find_one({"key":"meta"}) or {}
    meta["key"]="meta"; meta["roomPrices"]={"Diamond":diamond,"Gold":gold}; meta["payment"]=PAYMENT_INFO
    db.settings.replace_one({"key":"meta"}, meta, upsert=True)
    return redirect(url_for("admin_dashboard"))

# Seed admins (protected via token)
SEED_TOKEN = "letmeseednow"
@app.route("/seed_admins")
def seed_admins():
    if request.args.get("token") != SEED_TOKEN: return "Invalid token",403
    for e,p in ADMINS.items(): db.admins.update_one({"email":e},{"$set":{"email":e,"password":p}}, upsert=True)
    return "seeded"

@app.route("/health")
def health():
    try: _ = db.list_collection_names(); return jsonify({"status":"ok"})
    except Exception as e: return jsonify({"status":"error","detail":str(e)}),500

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000)); app.run(host="0.0.0.0", port=port, debug=False)
