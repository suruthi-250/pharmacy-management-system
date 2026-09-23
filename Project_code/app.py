from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import hashlib
import os
from datetime import date
from database import get_db, init_db
from threads import start_checker, get_alerts
from models import create_medicine
app = Flask(__name__)
app.secret_key = os.urandom(24)
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first!", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        # step 1: read username and password
        username = request.form["username"]
        password = request.form["password"]
        password = hash_pw(password)
        # step 2: check database
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        # step 3: if found → session → redirect
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        # step 4: if not found → flash error
        flash("Invalid username or password", "danger")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    # 1. clear the session
    session.clear()
    # 2. flash a goodbye message
    flash("Logged out successfully!", "info")
    # 3. redirect to login
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    # fetch 4 things from database:
    # 1. total number of medicines
    total = conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
    
    # 2. low stock count (quantity <= 10)
    low_stock = conn.execute("SELECT COUNT(*) FROM medicines WHERE quantity <= 10").fetchone()[0]
    
    # 3. expired count (expiry_date < today)
    expired =conn.execute("SELECT COUNT(*) FROM medicines WHERE DATE(expiry_date) < DATE('now')").fetchone()[0]
    
    # 4. expiring soon count (expiry_date within 30 days)
    expiring_soon =conn.execute("SELECT COUNT(*) FROM medicines WHERE DATE(expiry_date) BETWEEN DATE('now') AND DATE('now', '+30 days')").fetchone()[0]
    
    conn.close()
    
    alerts = get_alerts()
    
    return render_template("dashboard.html",
        total=total,
        low_stock=low_stock,
        expired=expired,
        expiring_soon=expiring_soon,
        alerts=alerts
    )

@app.route("/medicines")
@login_required
def medicines():
    search   = request.args.get("search", "")
    med_type = request.args.get("type", "")

    conn   = get_db()
    query  = "SELECT * FROM medicines WHERE 1=1"
    params = []

    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")
    if med_type:
        query += " AND type = ?"
        params.append(med_type)

    query += " ORDER BY name ASC"
    meds   = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("medicines.html", medicines=meds, search=search, med_type=med_type,now=date.today().strftime("%Y-%m-%d"))


@app.route("/medicines/add", methods=["GET", "POST"])
@login_required
def add_medicine():
    if request.method == "POST":
        name     = request.form["name"].strip()
        med_type = request.form["type"]
        quantity = int(request.form["quantity"])
        price    = float(request.form["price"])
        expiry   = request.form["expiry_date"]
        supplier = request.form["supplier"].strip()

        # validation
        if quantity < 0:
            flash("Quantity cannot be negative!", "danger")
            return render_template("medicine_form.html", medicine=None, editing=False)
        if price < 0:
            flash("Price cannot be negative!", "danger")
            return render_template("medicine_form.html", medicine=None, editing=False)

        # create OOP object (this is where models.py gets used!)
        med_obj = create_medicine(med_type, name, quantity, price, expiry, supplier)
        print(f"[OOP] {med_obj.get_type()} — {med_obj.get_info()} — Restricted: {med_obj.is_restricted()}")

        # save to database
        conn = get_db()
        conn.execute(
            "INSERT INTO medicines VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (name, med_type, quantity, price, expiry, supplier)
        )
        conn.commit()

        # audit log
        conn.execute(
            "INSERT INTO audit_log VALUES (NULL, ?, ?, ?, datetime('now'))",
            ("ADD", session["username"], f"Added medicine: {name}")
        )
        conn.commit()
        conn.close()

        flash(f"✅ {name} added successfully!", "success")
        return redirect(url_for("medicines"))

    return render_template("medicine_form.html", medicine=None, editing=False)


@app.route("/medicines/edit/<int:med_id>", methods=["GET", "POST"])
@login_required
def edit_medicine(med_id):
    conn = get_db()
    med  = conn.execute("SELECT * FROM medicines WHERE id=?", (med_id,)).fetchone()

    if not med:
        flash("Medicine not found!", "danger")
        return redirect(url_for("medicines"))

    if request.method == "POST":
        name     = request.form["name"].strip()
        med_type = request.form["type"]
        quantity = int(request.form["quantity"])
        price    = float(request.form["price"])
        expiry   = request.form["expiry_date"]
        supplier = request.form["supplier"].strip()

        conn.execute(
            "UPDATE medicines SET name=?, type=?, quantity=?, price=?, expiry_date=?, supplier=? WHERE id=?",
            (name, med_type, quantity, price, expiry, supplier, med_id)
        )
        conn.commit()

        # audit log
        conn.execute(
            "INSERT INTO audit_log VALUES (NULL, ?, ?, ?, datetime('now'))",
            ("EDIT", session["username"], f"Edited medicine: {name}")
        )
        conn.commit()
        conn.close()

        flash(f"✅ {name} updated!", "success")
        return redirect(url_for("medicines"))

    conn.close()
    return render_template("medicine_form.html", medicine=med, editing=True)


@app.route("/medicines/delete/<int:med_id>", methods=["POST"])
@login_required
def delete_medicine(med_id):
    if session.get("role") != "admin":
        flash("Only admin can delete medicines!", "danger")
        return redirect(url_for("medicines"))

    conn = get_db()
    med  = conn.execute("SELECT * FROM medicines WHERE id=?", (med_id,)).fetchone()
    conn.execute("DELETE FROM medicines WHERE id=?", (med_id,))
    conn.commit()

    # audit log
    conn.execute(
        "INSERT INTO audit_log VALUES (NULL, ?, ?, ?, datetime('now'))",
        ("DELETE", session["username"], f"Deleted medicine: {med['name']}")
    )
    conn.commit()
    conn.close()

    flash("Medicine deleted.", "warning")
    return redirect(url_for("medicines"))


@app.route("/alerts")
@login_required
def alerts():
    return render_template("alerts.html", alerts=get_alerts())

@app.route("/api/alerts")
@login_required
def api_alerts():
    return jsonify(get_alerts())

@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():
    conn  = get_db()
    meds  = conn.execute("SELECT * FROM medicines ORDER BY name ASC").fetchall()
    sales = conn.execute("""
        SELECT * FROM sales ORDER BY sold_at DESC
    """).fetchall()

    if request.method == "POST":
        med_id   = int(request.form["medicine_id"])
        quantity = int(request.form["quantity"])

        med = conn.execute("SELECT * FROM medicines WHERE id=?", (med_id,)).fetchone()

        # check if enough stock
        if quantity > med["quantity"]:
            flash(f"Not enough stock! Only {med['quantity']} left.", "danger")
            return render_template("sales.html", medicines=meds, sales=sales)

        if quantity <= 0:
            flash("Quantity must be greater than 0!", "danger")
            return render_template("sales.html", medicines=meds, sales=sales)

        total_price = quantity * med["price"]

        # reduce stock
        conn.execute(
            "UPDATE medicines SET quantity = quantity - ? WHERE id=?",
            (quantity, med_id)
        )

        # record sale
        conn.execute(
            "INSERT INTO sales VALUES (NULL, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (med_id, med["name"], quantity, med["price"], total_price, session["username"])
        )

        # audit log
        conn.execute(
            "INSERT INTO audit_log VALUES (NULL, ?, ?, ?, datetime('now'))",
            ("SALE", session["username"], f"Sold {quantity}x {med['name']} for ₹{total_price}")
        )

        conn.commit()
        conn.close()

        flash(f"✅ Sale recorded! ₹{total_price:.2f} total.", "success")
        return redirect(url_for("sales"))

    conn.close()
    return render_template("sales.html", medicines=meds, sales=sales)


@app.route("/audit")
@login_required
def audit():
    if session.get("role") != "admin":
        flash("Only admin can view audit logs!", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db()
    logs = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()

    return render_template("audit.html", logs=logs)


@app.route("/users")
@login_required
def users():
    if session.get("role") != "admin":
        flash("Only admin can manage users!", "danger")
        return redirect(url_for("dashboard"))

    conn  = get_db()
    users = conn.execute("SELECT id, username, role FROM users").fetchall()
    conn.close()

    return render_template("users.html", users=users)


@app.route("/users/add", methods=["GET", "POST"])
@login_required
def add_user():
    if session.get("role") != "admin":
        flash("Only admin can add users!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        role     = request.form["role"]

        if not username or not password:
            flash("Username and password cannot be empty!", "danger")
            return render_template("user_form.html")

        conn = get_db()
        existing = conn.execute(
            "SELECT 1 FROM users WHERE username=?", (username,)
        ).fetchone()

        if existing:
            flash("Username already exists!", "danger")
            conn.close()
            return render_template("user_form.html")

        conn.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?)",
            (username, hash_pw(password), role)
        )

        # audit log
        conn.execute(
            "INSERT INTO audit_log VALUES (NULL, ?, ?, ?, datetime('now'))",
            ("ADD USER", session["username"], f"Added new user: {username} as {role}")
        )

        conn.commit()
        conn.close()

        flash(f"✅ User {username} added!", "success")
        return redirect(url_for("users"))

    return render_template("user_form.html")


@app.route("/users/delete/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if session.get("role") != "admin":
        flash("Only admin can delete users!", "danger")
        return redirect(url_for("users"))

    if user_id == session["user_id"]:
        flash("You cannot delete yourself!", "danger")
        return redirect(url_for("users"))

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.execute(
        "INSERT INTO audit_log VALUES (NULL, ?, ?, ?, datetime('now'))",
        ("DELETE USER", session["username"], f"Deleted user ID: {user_id}")
    )
    conn.commit()
    conn.close()

    flash("User deleted.", "warning")
    return redirect(url_for("users"))

if __name__ == "__main__":
    init_db()
    start_checker()
    app.run(debug=True, port=5000)