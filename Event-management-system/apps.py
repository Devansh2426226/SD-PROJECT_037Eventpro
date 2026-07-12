import os
import sqlite3
from datetime import date, datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "eventpro-secret-key"

if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp") / "users.db"
else:
    DB_PATH = Path(__file__).with_name("users.db")
ADMIN_CREDENTIALS = {
    "Deepali": "deep36",
    "Devansh": "deva37",
    "Muskan": "musk59",
}
EVENTS = [
    {"title": "Music Concert", "date": "2026-08-20", "date_label": "20 August 2026", "location": "Lucknow Stadium", "price": "Entry from ₹1000", "image": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=800&q=80"},
    {"title": "Tech Fest", "date": "2026-08-28", "date_label": "28 August 2026", "location": "AKTU Campus", "price": "Entry from ₹500", "image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80"},
    {"title": "Food Festival", "date": "2026-09-05", "date_label": "5 September 2026", "location": "City Park", "price": "Entry from ₹300", "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80"},
    {"title": "Fashion Show", "date": "2026-09-12", "date_label": "12 September 2026", "location": "Convention Hall", "price": "Entry from ₹800", "image": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=800&q=80"},
    {"title": "Art Exhibition", "date": "2026-09-18", "date_label": "18 September 2026", "location": "Heritage Gallery", "price": "Entry from ₹450", "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=800&q=80"},
    {"title": "Wellness Retreat", "date": "2026-09-22", "date_label": "22 September 2026", "location": "Riverside Resort", "price": "Pass from ₹600", "image": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80"},
    {"title": "Startup Meetup", "date": "2026-09-27", "date_label": "27 September 2026", "location": "Co-Work Hub", "price": "Ticket from ₹350", "image": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=1600&q=80"},
    {"title": "Cultural Night", "date": "2026-10-03", "date_label": "3 October 2026", "location": "Royal Banquet Hall", "price": "Entry from ₹500", "image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=800&q=80"},
    {"title": "Charity Gala", "date": "2026-10-08", "date_label": "8 October 2026", "location": "Grand Ballroom", "price": "Contribution from ₹700", "image": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=800&q=80"},
    {"title": "Game Night", "date": "2026-10-14", "date_label": "14 October 2026", "location": "Lounge Street", "price": "Pass from ₹300", "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=800&q=80"},
    {"title": "Rooftop Brunch", "date": "2026-10-20", "date_label": "20 October 2026", "location": "Skyline Terrace", "price": "Seat from ₹550", "image": "https://images.unsplash.com/photo-1528605248644-14dd04022da1?auto=format&fit=crop&w=800&q=80"},
    {"title": "Kids Carnival", "date": "2026-10-25", "date_label": "25 October 2026", "location": "Family Fun Park", "price": "Entry from ₹400", "image": "https://images.unsplash.com/photo-1516627145497-ae6968895b74?auto=format&fit=crop&w=800&q=80"},
    {"title": "Dance Workshop", "date": "2026-10-30", "date_label": "30 October 2026", "location": "Studio 9", "price": "Workshop from ₹480", "image": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80"},
    {"title": "Film Screening", "date": "2026-11-05", "date_label": "5 November 2026", "location": "Open Air Cinema", "price": "Entry from ₹420", "image": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80"},
]


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            event TEXT NOT NULL,
            tickets TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def require_login():
    if "user_email" not in session:
        flash("Please log in to continue.", "info")
        return redirect(url_for("login"))
    return None


def get_featured_event():
    today = date.today()
    upcoming_events = []
    for event in EVENTS:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
        if event_date >= today:
            upcoming_events.append(event)

    if upcoming_events:
        return upcoming_events[0]
    return EVENTS[0]


@app.route("/")
def home():
    if "user_email" not in session:
        flash("Please log in to continue.", "info")
        return redirect(url_for("login"))
    return render_template(
        "index.html",
        user_email=session["user_email"],
        featured_event=get_featured_event(),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        conn.close()

        if user is not None and user["password"] == password:
            session["user_email"] = email
            return redirect(url_for("home"))

        flash("Invalid email or password. New users should register first.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not fullname or not email or not phone or not password or not confirm_password:
            flash("Please fill in all fields.", "danger")
        elif password != confirm_password:
            flash("Passwords do not match.", "danger")
        else:
            conn = get_db_connection()
            existing_user = conn.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,),
            ).fetchone()
            if existing_user:
                flash("This email is already registered. Please log in.", "warning")
            else:
                conn.execute(
                    "INSERT INTO users (fullname, email, phone, password) VALUES (?, ?, ?, ?)",
                    (fullname, email, phone, password),
                )
                conn.commit()
                conn.close()
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("login"))
            conn.close()

    return render_template("register.html")


@app.route("/events")
def events():
    redirect_result = require_login()
    if redirect_result is not None:
        return redirect_result

    today = date.today()
    event_list = []
    for event in EVENTS:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
        delta = (event_date - today).days
        if delta < 0:
            status = "Past Event"
            status_class = "past"
        elif delta == 0:
            status = "Happening Today"
            status_class = "today"
        elif delta == 1:
            status = "Starts Tomorrow"
            status_class = "soon"
        else:
            status = f"Starts in {delta} days"
            status_class = "upcoming"

        event_list.append({
            **event,
            "status": status,
            "status_class": status_class,
        })

    event_list.sort(key=lambda item: item["date"])
    return render_template("events.html", events=event_list)


@app.route("/booking")
def booking():
    redirect_result = require_login()
    if redirect_result is not None:
        return redirect_result
    return render_template("booking.html")


@app.route("/confirmation", methods=["POST"])
def confirmation():
    redirect_result = require_login()
    if redirect_result is not None:
        return redirect_result

    name = request.form.get("name", "")
    email = request.form.get("email", "")
    phone = request.form.get("phone", "")
    event = request.form.get("event", "")
    tickets = request.form.get("tickets", "")
    card_number = request.form.get("card_number", "")
    expiry = request.form.get("expiry", "")
    cvv = request.form.get("cvv", "")

    if not card_number or not expiry or not cvv:
        flash("Please complete the payment details to continue.", "danger")
        return redirect(url_for("booking"))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO bookings (name, email, phone, event, tickets) VALUES (?, ?, ?, ?, ?)",
        (name, email, phone, event, tickets),
    )
    conn.commit()
    conn.close()

    return render_template(
        "confirmation.html",
        name=name,
        email=email,
        phone=phone,
        event=event,
        tickets=tickets,
        card_number=card_number,
    )


@app.route("/about")
def about():
    redirect_result = require_login()
    if redirect_result is not None:
        return redirect_result
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    redirect_result = require_login()
    if redirect_result is not None:
        return redirect_result

    if request.method == "POST":
        return "Message sent successfully!"

    return render_template("contact.html")


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if ADMIN_CREDENTIALS.get(username) == password:
            session["admin_username"] = username
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials.", "danger")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("admin_username") is None:
        flash("Please log in as admin first.", "info")
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    users = conn.execute("SELECT id, fullname, email, phone FROM users ORDER BY id DESC").fetchall()
    bookings = conn.execute(
        "SELECT id, name, email, phone, event, tickets, created_at FROM bookings ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        bookings=bookings,
        username=session["admin_username"],
    )


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_username", None)
    flash("Admin logged out.", "info")
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True)