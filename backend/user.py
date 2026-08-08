from flask import Flask, request, render_template_string, send_from_directory, session, redirect
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-later"

DB = "study.db"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Study App</title>

<style>
body {
    font-family: Arial;
    background:#eef2f7;
    padding:20px;
}

.box {
    max-width:600px;
    margin:auto;
}

.card {
    background:white;
    padding:18px;
    margin:15px 0;
    border-radius:15px;
    box-shadow:0 3px 12px #ccc;
}

input, textarea, select, button {
    width:100%;
    box-sizing:border-box;
    padding:12px;
    margin:7px 0;
    border-radius:10px;
}

button {
    background:#222;
    color:white;
    border:0;
}

img {
    max-width:100%;
    border-radius:10px;
    margin-top:10px;
}

.post {
    border-top:1px solid #ddd;
    padding-top:12px;
    margin-top:12px;
}

.logout {
    display:block;
    text-align:center;
    margin:15px;
}
</style>
</head>

<body>

<div class="box">

<h1>📚 Study App</h1>

<h3>👋 Welcome {{username}}</h3>

<div class="card">

<h2>📤 Share Homework / Note</h2>

<form method="POST"
      action="/post"
      enctype="multipart/form-data">

<select name="type">

<option value="homework">🏠 Homework</option>
<option value="note">📝 Note</option>
<option value="announcement">📢 Announcement</option>

</select>

<input
name="title"
placeholder="Title"
required
>

<textarea
name="content"
placeholder="Write something..."
rows="5">
</textarea>

<input
type="file"
name="file"
accept="image/*,.pdf"
>

<button>
📤 Share With Everyone
</button>

</form>

</div>


<div class="card">

<h2>🌐 Shared By Students</h2>

{% for post in posts %}

<div class="post">

<b>👤 {{post["username"]}}</b>

<br>

<small>{{post["created_at"]}}</small>

<h3>{{post["title"]}}</h3>

<p>{{post["content"]}}</p>

{% if post["file_path"] %}

{% if post["file_path"].lower().endswith(
('.png','.jpg','.jpeg','.gif','.webp')
) %}

<img src="/uploads/{{post['file_path']}}">

{% else %}

<a href="/uploads/{{post['file_path']}}"
target="_blank">

📎 Open File

</a>

{% endif %}

{% endif %}

</div>

{% else %}

<p>No posts yet.</p>

{% endfor %}

</div>

<a class="logout" href="/logout">
🚪 Logout
</a>

</div>

</body>
</html>
"""


LOGIN = """
<!DOCTYPE html>
<html>
<head>

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>Student Login</title>

<style>

body {
    font-family:Arial;
    background:#eef2f7;
    padding:30px;
}

.box {
    max-width:420px;
    margin:auto;
    background:white;
    padding:25px;
    border-radius:18px;
}

input,button {
    width:100%;
    box-sizing:border-box;
    padding:14px;
    margin:8px 0;
}

button {
    background:#222;
    color:white;
    border:0;
    border-radius:10px;
}

.error {
    color:red;
}

</style>

</head>

<body>

<div class="box">

<h1>📚 Study App</h1>

<h2>👨‍🎓 Student Login</h2>

<form method="POST">

<input
name="name"
placeholder="Student Name"
required
>

<input
name="key"
placeholder="Access Key"
required
>

<button>
🔑 Login
</button>

</form>

<p class="error">{{message}}</p>

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():

    if "username" in session:
        return redirect("/home")

    if request.method == "POST":

        name = request.form.get("name")
        key = request.form.get("key")

        db = get_db()

        user = db.execute("""
        SELECT *
        FROM users
        WHERE name = ?
        AND access_key = ?
        """, (name, key)).fetchone()

        db.close()

        if not user:
            return render_template_string(
                LOGIN,
                message="❌ Invalid username or key"
            )

        if user["expiry"]:

            expiry = datetime.fromisoformat(
                user["expiry"]
            )

            if datetime.now() > expiry:
                return render_template_string(
                    LOGIN,
                    message="⏰ Your key has expired"
                )

        session["username"] = user["name"]

        return redirect("/home")

    return render_template_string(
        LOGIN,
        message=""
    )


@app.route("/home")
def home():

    if "username" not in session:
        return redirect("/")

    db = get_db()

    posts = db.execute("""
    SELECT *
    FROM shared_posts
    ORDER BY id DESC
    """).fetchall()

    db.close()

    return render_template_string(
        HTML,
        username=session["username"],
        posts=posts
    )


@app.route("/post", methods=["POST"])
def post():

    if "username" not in session:
        return redirect("/")

    title = request.form.get("title")
    content = request.form.get("content")
    post_type = request.form.get("type")

    uploaded = request.files.get("file")

    filename = None

    if uploaded and uploaded.filename:

        filename = uploaded.filename

        uploaded.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )

    db = get_db()

    db.execute("""
    INSERT INTO shared_posts
    (username, post_type, title,
     content, file_path, created_at)

    VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        session["username"],
        post_type,
        title,
        content,
        filename
    ))

    db.commit()
    db.close()

    return redirect("/home")


@app.route("/uploads/<filename>")
def uploads(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5002,
        debug=False
    )
