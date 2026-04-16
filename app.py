import os
from datetime import datetime
from functools import wraps

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "sportzone-secret-key")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@sportzone.com").strip().lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
STARTUP_INIT_DONE = False

SPORTS_DATA = [
    {
        "slug": "badminton",
        "name": "Badminton",
        "tagline": "Speed, precision, and lightweight control.",
        "hero": "Smash-ready equipment for matches, training, and tournament days.",
        "banner_class": "badminton",
        "products": [
            {"name": "Carbon Fiber Racket", "category": "Racket", "price": 7499.00, "stock": 18, "image": "static/images/racket.jpg", "description": "Balanced frame for powerful smashes with excellent wrist control."},
            {"name": "Tournament Shuttle Tubes", "category": "Shuttle", "price": 1999.00, "stock": 40, "image": "static/images/shuttle.jpg", "description": "Durable feather shuttles built for consistent flight and rally speed."},
            {"name": "Court Grip Shoes", "category": "Shoes", "price": 5399.00, "stock": 27, "image": "static/images/gripshoes.jpg", "description": "Non-marking sole with responsive cushioning for quick lateral movement."},
            {"name": "Performance Socks Pack", "category": "Socks", "price": 699.00, "stock": 60, "image": "static/images/socks.jpg", "description": "Breathable socks engineered for long indoor sessions."},
            {"name": "Racket Kit Bags", "category": "Bag", "price": 999.00, "stock": 60, "image": "static/images/bag.jpg", "description": "storing and transporting gear."},
            {"name": "Badminton Net", "category": "Net", "price": 2599.00, "stock": 30, "image": "static/images/net.jpg", "description": "Portable sets are available, along with standard steel posts and nylon nets."},
        ],
    },
    {
        "slug": "football",
        "name": "Football",
        "tagline": "Power, pace, and all-match durability.",
        "hero": "Gear up for training drills and match-winning weekends.",
        "banner_class": "football",
        "products": [
            {"name": "Match Football", "category": "Ball", "price": 2499.00, "stock": 22, "image": "static/images/football.jpg", "description": "FIFA-inspired training ball with dependable touch and flight."},
            {"name": "Speed Cleats", "category": "Shoes", "price": 6299.00, "stock": 16, "image": "static/images/cleats.jpg", "description": "Stud configuration optimized for acceleration and traction."},
            {"name": "Shin Guard Set", "category": "Protection", "price": 1499.00, "stock": 31, "image": "static/images/shin.jpg", "description": "Lightweight impact absorption for secure play on every tackle."},
            {"name": "Club Training Jersey", "category": "Apparel", "price": 2199.00, "stock": 45, "image": "static/images/jersey.jpg", "description": "Moisture-wicking jersey with athletic stretch."},
            {"name": "Goals and Nets:", "category": "Net", "price": 2199.00, "stock": 45, "image": "static/images/goals.jpg", "description": "Portable or permanent goals for shooting practice."},
            {"name": "Training Cones:", "category": "Cones", "price": 1199.00, "stock": 45, "image": "static/images/cones.jpg", "description": "Used to mark pitches or set up dribbling drills."},
        ],
    },
    {
        "slug": "cricket",
        "name": "Cricket",
        "tagline": "Classic essentials for nets, leagues, and street games.",
        "hero": "From bats to pads, every innings starts here.",
        "banner_class": "cricket",
        "products": [
            {"name": "English Willow Bat", "category": "Bat", "price": 10499.00, "stock": 14, "image": "static/images/bat.jpg", "description": "Well-balanced profile with strong pickup for front-foot strokes."},
            {"name": "Leather Cricket Ball", "category": "Ball", "price": 899.00, "stock": 34, "image": "static/images/leather.jpg", "description": "Match-style seam for practice and competitive sessions."},
            {"name": "Batting Gloves", "category": "Protection", "price": 2699.00, "stock": 25, "image": "static/images/gloves.jpg", "description": "Finger protection with premium palm grip for long innings."},
            {"name": "Leg Pad Pair", "category": "Pads", "price": 2299.00, "stock": 17, "image": "static/images/pad.jpg", "description": "Secure fit and shock diffusion against fast bowling."},
            {"name": "Stumps & Bails", "category": "stumps", "price": 4499.00, "stock": 17, "image": "static/images/bails.jpg", "description": "Three wooden uprights with two bails on top, forming the wicket"},
            {"name": "Kit Bag", "category": "kitbag", "price": 3999.00, "stock": 17, "image": "static/images/cricketbag.jpg", "description": "Duffle or wheelie bags to carry equipment."},
        ],
    },
    {
        "slug": "basketball",
        "name": "Basketball",
        "tagline": "Explosive energy for the court.",
        "hero": "High-grip, game-day gear for indoor and outdoor hoops.",
        "banner_class": "basketball",
        "products": [
            {"name": "Indoor/Outdoor Basketball", "category": "Ball", "price": 2299.00, "stock": 20, "image": "static/images/basketball.jpg", "description": "Deep channels and tacky grip for confident handling."},
            {"name": "Ankle Support Shoes", "category": "Shoes", "price": 7999.00, "stock": 19, "image": "static/images/ankleshoes.jpg", "description": "Responsive midsole with locked-in support for hard cuts and jumps."},
            {"name": "Compression Arm Sleeve", "category": "Accessory", "price": 899.00, "stock": 42, "image": "static/images/sleeve.jpg", "description": "Court-ready sleeve for warmth and muscle support."},
            {"name": "Training Cones Set", "category": "Cones", "price": 799.00, "stock": 36, "image": "static/images/coneset.jpg", "description": "Perfect for dribbling drills, agility ladders, and footwork sessions."},
            {"name": "Dribbling Goggles", "category": "Goggles", "price": 2999.00, "stock": 36, "image": "static/images/googles.jpg", "description": "These restrict vision to force players to look up while dribbling"},
            {"name": "Basketball Defender Dummy", "category": "Dummy", "price": 1599.00, "stock": 36, "image": "static/images/dummy.jpg", "description": "Simulates a defender for practicing high-arc shots."},
        ],
    },
    {
        "slug": "tennis",
        "name": "Tennis",
        "tagline": "Sharp control and all-court consistency.",
        "hero": "Premium gear for baseline battles and quick net play.",
        "banner_class": "tennis",
        "products": [
            {"name": "Graphite Tennis Racket", "category": "Racket", "price": 8899.00, "stock": 15, "image": "static/images/tennis.jpg", "description": "Spin-friendly frame with stable feel through impact."},
            {"name": "Pressurized Ball Can", "category": "Ball", "price": 999.00, "stock": 50, "image": "static/images/ballcan.jpg", "description": "Competition balls with lively bounce and durable felt."},
            {"name": "Clay Court Shoes", "category": "Shoes", "price": 6899.00, "stock": 18, "image": "static/images/clay.jpg", "description": "Stable herringbone outsole for confident sliding and recovery."},
            {"name": "Wristband Duo", "category": "Accessory", "price": 599.00, "stock": 55, "image": "static/images/duo.jpg", "description": "Soft absorbent wristbands for long rallies in the heat."},
            {"name": "Training Aids", "category": "Aids", "price": 2999.00, "stock": 15, "image": "static/images/aids.jpg", "description": "Training aids include ball pick-up tubes,"},
            {"name": "Nets", "category": "Nets", "price": 3399.00, "stock": 15, "image": "static/images/tennisnet.jpg", "description": "Portable pop-up nets are available for practice, alongside official-sized tennis nets."},
        ],
    },
]


def get_db():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"), serverSelectionTimeoutMS=5000)
    return client[os.getenv("MONGO_DB_NAME", "sportzone")]


db = get_db()


def serialize_id(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def normalize_image_path(image_value):
    if not image_value:
        return image_value
    if image_value.startswith("http://") or image_value.startswith("https://") or image_value.startswith("/static/"):
        return image_value
    if image_value.startswith("static/"):
        return f"/{image_value}"
    return image_value


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        session.pop("user_id", None)
        return None
    user = db.users.find_one({"_id": object_id})
    if not user:
        session.pop("user_id", None)
        return None
    return serialize_id(user) if user else None


def is_admin_user(user):
    return bool(user and user.get("role") == "admin")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to continue.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()
        if not is_admin_user(user):
            flash("Admin login required.", "error")
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def seed_database():
    if db.sports.count_documents({}) > 0:
        return
    for sport in SPORTS_DATA:
        sport_id = db.sports.insert_one({
            "slug": sport["slug"],
            "name": sport["name"],
            "tagline": sport["tagline"],
            "hero": sport["hero"],
            "banner_class": sport["banner_class"],
        }).inserted_id
        for product in sport["products"]:
            db.products.insert_one({"sport_id": sport_id, "sport_slug": sport["slug"], "sport_name": sport["name"], **product})


def sync_seed_products():
    sports_by_slug = {sport["slug"]: sport for sport in db.sports.find({}, {"_id": 1, "slug": 1, "name": 1})}
    for sport in SPORTS_DATA:
        sport_doc = sports_by_slug.get(sport["slug"])
        if not sport_doc:
            continue
        for product in sport["products"]:
            db.products.update_one(
                {"sport_slug": sport["slug"], "name": product["name"]},
                {
                    "$set": {
                        "sport_id": sport_doc["_id"],
                        "sport_slug": sport["slug"],
                        "sport_name": sport_doc["name"],
                        **product,
                    }
                },
                upsert=True,
            )


def seed_admin_user():
    admin = db.users.find_one({"email": ADMIN_EMAIL})
    if admin:
        if admin.get("role") != "admin":
            db.users.update_one({"_id": admin["_id"]}, {"$set": {"role": "admin"}})
        return
    db.users.insert_one({
        "full_name": "SportZone Admin",
        "email": ADMIN_EMAIL,
        "password_hash": generate_password_hash(ADMIN_PASSWORD),
        "favorite_sport": "Badminton",
        "role": "admin",
        "created_at": datetime.utcnow(),
    })


def initialize_app_data():
    global STARTUP_INIT_DONE
    if STARTUP_INIT_DONE:
        return
    seed_database()
    sync_seed_products()
    seed_admin_user()
    STARTUP_INIT_DONE = True


@app.context_processor
def inject_globals():
    cart = session.get("cart", {})
    return {
        "cart_count": sum(int(item.get("quantity", 0)) for item in cart.values()),
        "year": datetime.utcnow().year,
        "current_user": get_current_user(),
    }


def get_sports_with_products():
    sports = list(db.sports.find().sort("name", 1))
    for sport in sports:
        products = list(db.products.find({"sport_id": sport["_id"]}).sort([("category", 1), ("name", 1)]))
        for product in products:
            product["image"] = normalize_image_path(product.get("image"))
            serialize_id(product)
        sport["products"] = products
        serialize_id(sport)
    return sports


def get_cart_products():
    items = []
    for product_id, meta in session.get("cart", {}).items():
        product = db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            continue
        product["image"] = normalize_image_path(product.get("image"))
        quantity = int(meta.get("quantity", 1))
        items.append({"product": serialize_id(product), "quantity": quantity, "subtotal": round(product["price"] * quantity, 2)})
    return items


def get_payment_options():
    return [
        {"value": "card", "label": "Credit / Debit Card"},
        {"value": "upi", "label": "UPI"},
        {"value": "cod", "label": "Cash on Delivery"},
    ]


def get_latest_customer_profile(user_id):
    if not user_id:
        return None
    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None
    profile = db.customers.find_one({"user_id": object_id}, sort=[("created_at", -1)])
    return serialize_id(profile) if profile else None


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if get_current_user():
        return redirect(url_for("home"))
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        favorite_sport = request.form["favorite_sport"].strip()

        if db.users.find_one({"email": email}):
            flash("An account with this email already exists.", "error")
            return redirect(url_for("signup"))

        user_id = db.users.insert_one({
            "full_name": full_name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "favorite_sport": favorite_sport,
            "role": "customer",
            "created_at": datetime.utcnow(),
        }).inserted_id
        session["user_id"] = str(user_id)
        flash("Signup successful. You are now logged in.", "success")
        return redirect(url_for("home"))
    sports = [serialize_id(sport) for sport in list(db.sports.find().sort("name", 1))]
    return render_template("auth.html", mode="signup", sports=sports)


@app.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user():
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = db.users.find_one({"email": email})

        if user and user.get("role") == "admin":
            flash("Please use the admin login page for admin access.", "error")
            return redirect(url_for("admin_login"))

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = str(user["_id"])
        flash(f"Welcome back, {user['full_name']}.", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("home"))
    return render_template("auth.html", mode="login", sports=[])


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    user = get_current_user()
    if is_admin_user(user):
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = db.users.find_one({"email": email, "role": "admin"})

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid admin email or password.", "error")
            return redirect(url_for("admin_login"))

        session["user_id"] = str(user["_id"])
        flash("Admin login successful.", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("admin_dashboard"))
    return render_template("auth.html", mode="admin", sports=[])


@app.post("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    current_user = get_current_user()
    customer_profile = get_latest_customer_profile(current_user["_id"])
    return render_template("profile.html", customer_profile=customer_profile)


@app.route("/")
def home():
    sports = get_sports_with_products()
    featured_products = list(db.products.find().sort("price", -1).limit(6))
    for product in featured_products:
        product["image"] = normalize_image_path(product.get("image"))
        serialize_id(product)
    return render_template("index.html", sports=sports, featured_products=featured_products)


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.route("/sport/<slug>")
def sport_detail(slug):
    sport = db.sports.find_one({"slug": slug})
    if not sport:
        flash("Sport category not found.", "error")
        return redirect(url_for("home"))
    products = list(db.products.find({"sport_slug": slug}).sort([("category", 1), ("price", 1)]))
    serialize_id(sport)
    for product in products:
        product["image"] = normalize_image_path(product.get("image"))
        serialize_id(product)
    return render_template("sport_detail.html", sport=sport, products=products)


@app.post("/add-to-cart/<product_id>")
def add_to_cart(product_id):
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found.", "error")
        return redirect(request.referrer or url_for("home"))
    cart = session.get("cart", {})
    current = cart.get(product_id, {"quantity": 0})
    cart[product_id] = {"quantity": current["quantity"] + 1}
    session["cart"] = cart
    session.modified = True
    flash(f"{product['name']} added to cart.", "success")
    return redirect(request.referrer or url_for("home"))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    if request.method == "POST":
        cart_state = session.get("cart", {})
        for field_name, value in request.form.items():
            if not field_name.startswith("qty_"):
                continue
            item_id = field_name.replace("qty_", "", 1)
            quantity = max(0, int(value or 0))
            if quantity == 0:
                cart_state.pop(item_id, None)
            elif item_id in cart_state:
                cart_state[item_id]["quantity"] = quantity
        session["cart"] = cart_state
        session.modified = True
        flash("Cart updated.", "success")
        return redirect(url_for("cart"))
    items = get_cart_products()
    return render_template("cart.html", items=items, total=round(sum(item["subtotal"] for item in items), 2))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = get_cart_products()
    total = round(sum(item["subtotal"] for item in items), 2)
    current_user = get_current_user()
    payment_options = get_payment_options()
    if not items:
        flash("Your cart is empty. Add products before checkout.", "error")
        return redirect(url_for("home"))
    if request.method == "POST":
        payment_method = request.form["payment_method"].strip()
        payment_map = {option["value"]: option["label"] for option in payment_options}
        if payment_method not in payment_map:
            flash("Please select a valid payment method.", "error")
            return redirect(url_for("checkout"))

        card_name = request.form.get("card_name", "").strip()
        card_number = request.form.get("card_number", "").strip()
        upi_id = request.form.get("upi_id", "").strip()

        if payment_method == "card" and (not card_name or len(card_number) < 4):
            flash("Please enter cardholder name and card number.", "error")
            return redirect(url_for("checkout"))
        if payment_method == "upi" and not upi_id:
            flash("Please enter your UPI ID.", "error")
            return redirect(url_for("checkout"))

        payment_details = {
            "method": payment_method,
            "method_label": payment_map[payment_method],
            "status": "Paid" if payment_method in {"card", "upi"} else "Pending on Delivery",
            "reference": (
                f"****{card_number[-4:]}" if payment_method == "card" else upi_id if payment_method == "upi" else "Cash collection at delivery"
            ),
        }

        customer = {
            "full_name": request.form["full_name"].strip(),
            "email": request.form["email"].strip().lower(),
            "phone": request.form["phone"].strip(),
            "address": request.form["address"].strip(),
            "city": request.form["city"].strip(),
            "postal_code": request.form["postal_code"].strip(),
            "favorite_sport": request.form["favorite_sport"].strip(),
            "user_id": ObjectId(current_user["_id"]),
            "created_at": datetime.utcnow(),
        }
        customer_id = db.customers.insert_one(customer).inserted_id
        db.orders.insert_one({
            "customer_id": customer_id,
            "user_id": ObjectId(current_user["_id"]),
            "admin_status": "New Lead",
            "customer_name": customer["full_name"],
            "customer_email": customer["email"],
            "items": [{"product_id": ObjectId(item["product"]["_id"]), "product_name": item["product"]["name"], "sport_name": item["product"]["sport_name"], "quantity": item["quantity"], "unit_price": item["product"]["price"], "subtotal": item["subtotal"]} for item in items],
            "total": total,
            "payment": payment_details,
            "notes": request.form.get("notes", "").strip(),
            "created_at": datetime.utcnow(),
        })
        session["cart"] = {}
        session.modified = True
        flash(f"Order placed successfully with {payment_details['method_label']}. Customer details are now stored for the admin.", "success")
        return redirect(url_for("thank_you"))
    sports = [serialize_id(sport) for sport in list(db.sports.find().sort("name", 1))]
    return render_template(
        "checkout.html",
        items=items,
        total=total,
        sports=sports,
        current_user=current_user,
        payment_options=payment_options,
    )


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


@app.route("/admin")
@admin_required
def admin_dashboard():
    customers = list(db.customers.find().sort("created_at", -1))
    orders = list(db.orders.find().sort("created_at", -1))
    for customer in customers:
        serialize_id(customer)
    for order in orders:
        serialize_id(order)
    metrics = {
        "sports": db.sports.count_documents({}),
        "products": db.products.count_documents({}),
        "customers": db.customers.count_documents({}),
        "orders": db.orders.count_documents({}),
        "sales": round(sum(order.get("total", 0) for order in db.orders.find({}, {"total": 1, "_id": 0})), 2),
    }
    return render_template("operator.html", customers=customers, orders=orders, metrics=metrics)


@app.route("/operator")
def operator_dashboard():
    return redirect(url_for("admin_dashboard"))

initialize_app_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
