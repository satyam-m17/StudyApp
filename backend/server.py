from flask import Flask, request, jsonify
import sqlite3
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)

DB = "study.db"


# =========================
# DATABASE
# =========================

def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():

    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        access_key TEXT UNIQUE NOT NULL,
        key_type TEXT NOT NULL,
        expiry TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS homework (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)

    db.commit()
    db.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return jsonify({
        "app": "Study App",
        "status": "Backend is running"
    })


# =========================
# GENERATE KEY
# =========================

@app.route("/admin/generate-key", methods=["POST"])
def generate_key():

    data = request.get_json()

    name = data.get("name")
    key_type = data.get("type")

    if not name or key_type not in ["1h", "10d", "life"]:
        return jsonify({
            "error": "Invalid name or key type"
        }), 400

    key = secrets.token_hex(5).upper()

    now = datetime.now()

    if key_type == "1h":
        expiry = now + timedelta(hours=1)

    elif key_type == "10d":
        expiry = now + timedelta(days=10)

    else:
        expiry = None

    db = get_db()

    db.execute(
        """
        INSERT INTO users
        (name, access_key, key_type, expiry)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            key,
            key_type,
            expiry.isoformat() if expiry else None
        )
    )

    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "name": name,
        "key": key,
        "type": key_type,
        "expiry": expiry.isoformat() if expiry else "Lifetime"
    })


# =========================
# STUDENT LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    name = data.get("name")
    key = data.get("key")

    db = get_db()

    user = db.execute(
        """
        SELECT * FROM users
        WHERE access_key = ? AND name = ?
        """,
        (key, name)
    ).fetchone()

    db.close()

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid name or key"
        }), 401

    if user["expiry"]:

        expiry = datetime.fromisoformat(user["expiry"])

        if datetime.now() > expiry:
            return jsonify({
                "success": False,
                "message": "Key expired"
            }), 401

    return jsonify({
        "success": True,
        "message": "Login successful",
        "name": user["name"],
        "key_type": user["key_type"]
    })


# =========================
# ADD NOTE
# =========================

@app.route("/admin/add-note", methods=["POST"])
def add_note():

    data = request.get_json()

    subject = data.get("subject")
    title = data.get("title")
    content = data.get("content")

    if not subject or not title or not content:
        return jsonify({
            "error": "All fields are required"
        }), 400

    db = get_db()

    db.execute(
        """
        INSERT INTO notes
        (subject, title, content)
        VALUES (?, ?, ?)
        """,
        (subject, title, content)
    )

    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "message": "Note added"
    })


# =========================
# GET NOTES
# =========================

@app.route("/notes")
def notes():

    db = get_db()

    rows = db.execute(
        "SELECT * FROM notes ORDER BY id DESC"
    ).fetchall()

    db.close()

    return jsonify([
        dict(row) for row in rows
    ])


# =========================
# ADD HOMEWORK
# =========================

@app.route("/admin/add-homework", methods=["POST"])
def add_homework():

    data = request.get_json()

    subject = data.get("subject")
    title = data.get("title")
    content = data.get("content")

    if not subject or not title or not content:
        return jsonify({
            "error": "All fields are required"
        }), 400

    db = get_db()

    db.execute(
        """
        INSERT INTO homework
        (subject, title, content)
        VALUES (?, ?, ?)
        """,
        (subject, title, content)
    )

    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "message": "Homework added"
    })


# =========================
# GET HOMEWORK
# =========================

@app.route("/homework")
def homework():

    db = get_db()

    rows = db.execute(
        "SELECT * FROM homework ORDER BY id DESC"
    ).fetchall()

    db.close()

    return jsonify([
        dict(row) for row in rows
    ])


# =========================
# START
# =========================

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
