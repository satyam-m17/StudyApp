from flask import Flask, request, render_template_string, redirect, session, send_from_directory
import sqlite3
import os
import secrets
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET"

DB = "study.db"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ADMIN_PASSWORD = "admin123"


# =========================
# DATABASE
# =========================

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        access_key TEXT UNIQUE NOT NULL,
        key_type TEXT NOT NULL,
        expiry TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        post_type TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        file_path TEXT,
        created_at TEXT NOT NULL
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS homework (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# =========================
# COMMON STYLE
# =========================

STYLE = """
<style>

body {
    font-family: Arial;
    background:#eef2f7;
    padding:20px;
}

.box {
    max-width:700px;
    margin:auto;
}

.card {
    background:white;
    padding:20px;
    margin:15px 0;
    border-radius:16px;
    box-shadow:0 3px 12px #ccc;
}

input, textarea, select, button {
    width:100%;
    box-sizing:border-box;
    padding:13px;
    margin:7px 0;
    border-radius:10px;
}

button {
    background:#222;
    color:white;
    border:0;
}

a {
    text-decoration:none;
}

.post {
    border-top:1px solid #ddd;
    padding-top:12px;
    margin-top:12px;
}

img {
    max-width:100%;
    border-radius:10px;
    margin-top:10px;
}

.key {
    background:#f1f1f1;
    padding:12px;
    margin:10px 0;
    border-radius:10px;
}

</style>
"""


# =========================
# LOGIN
# =========================

LOGIN = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Study App</title>
""" + STYLE + """
</head>

<body>

<div class="box">

<div class="card">

<h1>📚 Study App</h1>

<h2>👨‍🎓 Student Login</h2>

<form method="POST">

<input
name="name"
placeholder="Student Name"
required>

<input
name="key"
placeholder="Access Key"
required>

<button>🔑 Login</button>

</form>

<p>{{message}}</p>

<hr>

<a href="/admin">👑 Admin Panel</a>

</div>

</div>

</body>
</html>
"""


# =========================
# USER PANEL
# =========================

USER = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>User Panel</title>
""" + STYLE + """
</head>

<body>

<div class="box">

<h1>👨‍🎓 Welcome {{username}} 👋</h1>

<div class="card">

<h2>📝 Notes</h2>

{% for n in notes %}

<div class="post">

<b>{{n["subject"]}}</b>

<h3>{{n["title"]}}</h3>

<p>{{n["content"]}}</p>

</div>

{% else %}

<p>No notes yet.</p>

{% endfor %}

</div>


<div class="card">

<h2>🏠 Homework</h2>

{% for h in homework %}

<div class="post">

<b>{{h["subject"]}}</b>

<h3>{{h["title"]}}</h3>

<p>{{h["content"]}}</p>

</div>

{% else %}

<p>No homework yet.</p>

{% endfor %}

</div>


<div class="card">

<h2>📤 Share Homework / Note</h2>

<form method="POST"
action="/post"
enctype="multipart/form-data">

<select name="type">

<option value="homework">🏠 Homework</option>
<option value="note">📝 Note</option>

</select>

<input
name="title"
placeholder="Title"
required>

<textarea
name="content"
placeholder="Write something..."
rows="5"></textarea>

<input
type="file"
name="file"
accept="image/*,.pdf">

<button>
📤 Share With Everyone
</button>

</form>

</div>


<div class="card">

<h2>🌐 Shared By Students</h2>

{% for p in posts %}

<div class="post">

<b>👤 {{p["username"]}}</b>

<br>

<small>{{p["created_at"]}}</small>

<h3>{{p["title"]}}</h3>

<p>{{p["content"]}}</p>

{% if p["file_path"] %}

{% if p["file_path"].lower().endswith(
('.png','.jpg','.jpeg','.gif','.webp')
) %}

<img src="/uploads/{{p['file_path']}}">

{% else %}

<a href="/uploads/{{p['file_path']}}"
target="_blank">
📎 Open File
</a>

{% endif %}

{% endif %}

</div>

{% endfor %}

</div>


<a href="/logout">🚪 Logout</a>

</div>

</body>
</html>
"""


# =========================
# ADMIN LOGIN
# =========================

ADMIN_LOGIN = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin Login</title>
""" + STYLE + """
</head>

<body>

<div class="box">

<div class="card">

<h1>👑 Admin Login</h1>

<form method="POST">

<input
type="password"
name="password"
placeholder="Admin Password"
required>

<button>Login</button>

</form>

<p>{{message}}</p>

</div>

</div>

</body>
</html>
"""


# =========================
# ADMIN PANEL
# =========================

ADMIN = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin Panel</title>
""" + STYLE + """
</head>

<body>

<div class="box">

<h1>👑 Admin Panel</h1>


<div class="card">

<h2>🔑 Generate Key</h2>

<form method="POST"
action="/generate">

<input
name="name"
placeholder="Student Name"
required>

<select name="duration">

<option value="1h">1 Hour</option>
<option value="10d">10 Days</option>
<option value="life">Lifetime</option>

</select>

<button>✨ Generate Key</button>

</form>

</div>


<div class="card">

<h2>📋 Generated Keys</h2>

{% for k in keys %}

<div class="key">

👤 {{k["name"]}}

<br>

🔑 <b>{{k["access_key"]}}</b>

<br>

⏳ {{k["key_type"]}}

<br>

Expiry:
{{k["expiry"] or "Lifetime"}}

</div>

{% else %}

<p>No keys yet.</p>

{% endfor %}

</div>


<div class="card">

<h2>📝 Add Note</h2>

<form method="POST" action="/admin/note">

<select name="subject">

<option>Accountancy</option>
<option>Business Studies</option>
<option>Statistics</option>
<option>Micro Economics</option>
<option>English</option>
<option>Physical Education</option>

</select>

<input
name="title"
placeholder="Note Title"
required>

<textarea
name="content"
placeholder="Note content"
required></textarea>

<button>➕ Add Note</button>

</form>

</div>


<div class="card">

<h2>🏠 Add Homework</h2>

<form method="POST" action="/admin/homework">

<select name="subject">

<option>Accountancy</option>
<option>Business Studies</option>
<option>Statistics</option>
<option>Micro Economics</option>
<option>English</option>
<option>Physical Education</option>

</select>

<input
name="title"
placeholder="Homework Title"
required>

<textarea
name="content"
placeholder="Homework details"
required></textarea>

<button>➕ Add Homework</button>

</form>

</div>


<div class="card">

<h2>🌐 Student Shared Posts</h2>

{% for p in posts %}

<div class="post">

👤 <b>{{p["username"]}}</b>

<br>

{{p["title"]}}

<br>

{{p["content"]}}

</div>

{% endfor %}

</div>

</div>

</body>
</html>
"""


# =========================
# STUDENT LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if "username" in session:
        return redirect("/home")

    if request.method == "POST":

        name = request.form["name"]
        key = request.form["key"]

        conn = db()

        user = conn.execute("""
        SELECT *
        FROM users
        WHERE name = ?
        AND access_key = ?
        """, (name, key)).fetchone()

        conn.close()

        if not user:

            return render_template_string(
                LOGIN,
                message="❌ Invalid name or key"
            )

        if user["expiry"]:

            expiry = datetime.fromisoformat(
                user["expiry"]
            )

            if datetime.now() > expiry:

                return render_template_string(
                    LOGIN,
                    message="⏰ Key expired"
                )

        session["username"] = user["name"]

        return redirect("/home")

    return render_template_string(
        LOGIN,
        message=""
    )


# =========================
# USER HOME
# =========================

@app.route("/home")
def home():

    if "username" not in session:
        return redirect("/")

    conn = db()

    posts = conn.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()

    notes = conn.execute(
        "SELECT * FROM notes ORDER BY id DESC"
    ).fetchall()

    homework = conn.execute(
        "SELECT * FROM homework ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template_string(
        USER,
        username=session["username"],
        posts=posts,
        notes=notes,
        homework=homework
    )


# =========================
# USER POST
# =========================

@app.route("/post", methods=["POST"])
def post():

    if "username" not in session:
        return redirect("/")

    title = request.form["title"]
    content = request.form.get("content", "")
    post_type = request.form["type"]

    file = request.files.get("file")

    filename = None

    if file and file.filename:

        filename = secure_filename(
            file.filename
        )

        filename = (
            secrets.token_hex(6)
            + "_"
            + filename
        )

        file.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )

    conn = db()

    conn.execute("""
    INSERT INTO posts
    (username, post_type, title,
     content, file_path, created_at)

    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session["username"],
        post_type,
        title,
        content,
        filename,
        datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )
    ))

    conn.commit()
    conn.close()

    return redirect("/home")


# =========================
# UPLOADS
# =========================

@app.route("/uploads/<filename>")
def uploads(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        if request.form["password"] != ADMIN_PASSWORD:

            return render_template_string(
                ADMIN_LOGIN,
                message="❌ Wrong password"
            )

        session["admin"] = True

        return redirect("/admin/panel")

    return render_template_string(
        ADMIN_LOGIN,
        message=""
    )


# =========================
# ADMIN PANEL
# =========================

@app.route("/admin/panel")
def admin_panel():

    if not session.get("admin"):
        return redirect("/admin")

    conn = db()

    keys = conn.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    posts = conn.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template_string(
        ADMIN,
        keys=keys,
        posts=posts
    )


# =========================
# GENERATE KEY
# =========================

@app.route("/generate", methods=["POST"])
def generate():

    if not session.get("admin"):
        return redirect("/admin")

    name = request.form["name"]
    duration = request.form["duration"]

    key = secrets.token_hex(5).upper()

    now = datetime.now()

    if duration == "1h":

        expiry = now + timedelta(hours=1)

    elif duration == "10d":

        expiry = now + timedelta(days=10)

    else:

        expiry = None

    conn = db()

    conn.execute("""
    INSERT INTO users
    (name, access_key, key_type, expiry)

    VALUES (?, ?, ?, ?)
    """, (
        name,
        key,
        duration,
        expiry.isoformat() if expiry else None
    ))

    conn.commit()
    conn.close()

    return redirect("/admin/panel")


# =========================
# ADMIN NOTE
# =========================

@app.route("/admin/note", methods=["POST"])
def add_note():

    if not session.get("admin"):
        return redirect("/admin")

    conn = db()

    conn.execute("""
    INSERT INTO notes
    (subject, title, content)

    VALUES (?, ?, ?)
    """, (
        request.form["subject"],
        request.form["title"],
        request.form["content"]
    ))

    conn.commit()
    conn.close()

    return redirect("/admin/panel")


# =========================
# ADMIN HOMEWORK
# =========================

@app.route("/admin/homework", methods=["POST"])
def add_homework():

    if not session.get("admin"):
        return redirect("/admin")

    conn = db()

    conn.execute("""
    INSERT INTO homework
    (subject, title, content)

    VALUES (?, ?, ?)
    """, (
        request.form["subject"],
        request.form["title"],
        request.form["content"]
    ))

    conn.commit()
    conn.close()

    return redirect("/admin/panel")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# START
# =========================

init_db()

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
