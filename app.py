from flask import Flask, request, render_template_string
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)

# =========================
# ADMIN SETTINGS
# =========================

ADMIN_PASSWORD = "admin123"

# Demo keys
keys = {
    "STUDENT123": {
        "name": "Satyam",
        "type": "10d",
        "created": datetime.now(),
        "expiry": datetime.now() + timedelta(days=10)
    }
}


# =========================
# LOGIN PAGE
# =========================

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Study App</title>

<style>
body {
    font-family: Arial;
    background: #eef2f7;
    padding: 30px;
}

.box {
    max-width: 420px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 5px 20px #ccc;
}

input, button {
    width: 100%;
    padding: 14px;
    margin: 8px 0;
    box-sizing: border-box;
    border-radius: 10px;
}

button {
    border: none;
    font-size: 16px;
}

.login {
    background: #222;
    color: white;
}

.admin {
    display: block;
    text-align: center;
    margin-top: 20px;
}
</style>
</head>

<body>

<div class="box">

<h1>📚 Study App</h1>

<h2>Student Login</h2>

<form method="POST">

<input
name="username"
placeholder="Student Name"
required
>

<input
name="key"
placeholder="Access Key"
required
>

<button class="login">🔑 Login</button>

</form>

<p>{{ message }}</p>

<a class="admin" href="/admin">
👑 Admin Panel
</a>

</div>

</body>
</html>
"""


# =========================
# USER PANEL
# =========================

USER_PAGE = """
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>User Panel</title>

<style>

body {
    font-family: Arial;
    background: #eef2f7;
    padding: 20px;
}

.box {
    max-width: 550px;
    margin: auto;
}

.card {
    background: white;
    padding: 20px;
    margin: 15px 0;
    border-radius: 15px;
    box-shadow: 0 3px 12px #ccc;
}

.subject {
    padding: 8px;
}

</style>

</head>

<body>

<div class="box">

<h1>👨‍🎓 User Panel</h1>

<h3>
Welcome {{ name }} 👋
</h3>


<div class="card">

<h2>📝 Notes</h2>

<p>
Notes देखने और submit करने का section
</p>

</div>


<div class="card">

<h2>📚 Fair Copy</h2>

<div class="subject">📒 Accountancy</div>
<div class="subject">📗 Business Studies</div>
<div class="subject">📘 Statistics</div>
<div class="subject">📙 Micro Economics</div>
<div class="subject">📕 English</div>
<div class="subject">📓 Physical Education</div>

</div>


<div class="card">

<h2>🏠 Homework</h2>

<div class="subject">📒 Accountancy</div>
<div class="subject">📗 Business Studies</div>
<div class="subject">📘 Statistics</div>
<div class="subject">📙 Micro Economics</div>
<div class="subject">📕 English</div>
<div class="subject">📓 Physical Education</div>

</div>


<div class="card">

<h2>💬 Chat</h2>

<p>👥 Chat with Students</p>

<p>👑 Chat with Admin</p>

</div>


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

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Admin Login</title>

<style>

body {
    font-family: Arial;
    background: #eef2f7;
    padding: 30px;
}

.box {
    max-width: 420px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
}

input, button {
    width: 100%;
    padding: 14px;
    margin: 8px 0;
    box-sizing: border-box;
}

button {
    background: #222;
    color: white;
    border: none;
    border-radius: 10px;
}

</style>

</head>

<body>

<div class="box">

<h1>👑 Admin Login</h1>

<form method="POST">

<input
type="password"
name="password"
placeholder="Admin Password"
required
>

<button>
Login
</button>

</form>

<p>{{ message }}</p>

</div>

</body>
</html>
"""


# =========================
# ADMIN PANEL
# =========================

ADMIN_PANEL = """
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Admin Panel</title>

<style>

body {
    font-family: Arial;
    background: #eef2f7;
    padding: 20px;
}

.box {
    max-width: 650px;
    margin: auto;
}

.card {
    background: white;
    padding: 20px;
    margin: 15px 0;
    border-radius: 15px;
    box-shadow: 0 3px 12px #ccc;
}

input, select, button {
    width: 100%;
    padding: 13px;
    margin: 7px 0;
    box-sizing: border-box;
}

button {
    background: #222;
    color: white;
    border: none;
    border-radius: 10px;
}

.key {
    background: #f1f1f1;
    padding: 12px;
    margin: 10px 0;
    border-radius: 10px;
}

</style>

</head>

<body>

<div class="box">

<h1>👑 Admin Panel</h1>


<div class="card">

<h2>🔑 Generate Student Key</h2>

<form method="POST"
action="/generate">

<input
name="student"
placeholder="Student Name"
required
>

<select name="duration">

<option value="1h">
1 Hour
</option>

<option value="10d">
10 Days
</option>

<option value="life">
Lifetime
</option>

</select>

<button>
✨ Generate Key
</button>

</form>

</div>


<div class="card">

<h2>📋 Generated Keys</h2>

{% for key, data in keys.items() %}

<div class="key">

👤 <b>
{{ data.name }}
</b>

<br>

🔑
<b>
{{ key }}
</b>

<br>

⏳
{{ data.expiry_text }}

</div>

{% else %}

<p>
No keys generated.
</p>

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

    if request.method == "POST":

        username = request.form.get("username")
        key = request.form.get("key")

        if key not in keys:

            return render_template_string(
                LOGIN_PAGE,
                message="❌ Invalid Key"
            )

        data = keys[key]

        if data["name"].lower() != username.lower():

            return render_template_string(
                LOGIN_PAGE,
                message="❌ Username does not match this key"
            )

        if data["expiry"] is not None:

            if datetime.now() > data["expiry"]:

                return render_template_string(
                    LOGIN_PAGE,
                    message="⏰ This key has expired"
                )

        return render_template_string(
            USER_PAGE,
            name=data["name"]
        )

    return render_template_string(
        LOGIN_PAGE,
        message=""
    )


# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        password = request.form.get("password")

        if password != ADMIN_PASSWORD:

            return render_template_string(
                ADMIN_LOGIN,
                message="❌ Wrong Admin Password"
            )

        return render_template_string(
            ADMIN_PANEL,
            keys=keys
        )

    return render_template_string(
        ADMIN_LOGIN,
        message=""
    )


# =========================
# GENERATE KEY
# =========================

@app.route("/generate", methods=["POST"])
def generate():

    student = request.form.get("student")
    duration = request.form.get("duration")

    key = secrets.token_hex(4).upper()

    created = datetime.now()

    if duration == "1h":

        expiry = created + timedelta(hours=1)

        expiry_text = expiry.strftime(
            "%d-%m-%Y %I:%M %p"
        )

    elif duration == "10d":

        expiry = created + timedelta(days=10)

        expiry_text = expiry.strftime(
            "%d-%m-%Y %I:%M %p"
        )

    else:

        expiry = None
        expiry_text = "Lifetime"


    keys[key] = {
        "name": student,
        "type": duration,
        "created": created,
        "expiry": expiry,
        "expiry_text": expiry_text
    }


    return render_template_string(
        ADMIN_PANEL,
        keys=keys
    )


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
