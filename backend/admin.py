from flask import Flask, request, jsonify
import sqlite3
import secrets
from datetime import datetime

app = Flask(__name__)

DB = "study.db"


def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


# Shared posts table
def init_db():

    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS shared_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        post_type TEXT NOT NULL,
        title TEXT,
        content TEXT,
        file_path TEXT,
        created_at TEXT NOT NULL
    )
    """)

    db.commit()
    db.close()


# Home
@app.route("/")
def home():

    return jsonify({
        "status": "Admin backend running"
    })


# Create shared post
@app.route("/post", methods=["POST"])
def create_post():

    data = request.get_json()

    username = data.get("username")
    post_type = data.get("type")
    title = data.get("title", "")
    content = data.get("content", "")

    if not username or not post_type:
        return jsonify({
            "error": "Username and post type required"
        }), 400

    db = get_db()

    db.execute("""
    INSERT INTO shared_posts
    (username, post_type, title, content, file_path, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        post_type,
        title,
        content,
        None,
        datetime.now().isoformat()
    ))

    db.commit()
    db.close()

    return jsonify({
        "success": True,
        "message": "Post shared with all users"
    })


# Get all shared posts
@app.route("/posts")
def get_posts():

    db = get_db()

    posts = db.execute("""
    SELECT *
    FROM shared_posts
    ORDER BY id DESC
    """).fetchall()

    db.close()

    return jsonify([
        dict(post) for post in posts
    ])


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )
