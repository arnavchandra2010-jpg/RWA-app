from flask import flask , render_templates
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from functools import wraps
from werkzeug.security import check_password_hash

app = flask(__name__)
app.secret_key = "NOT THE ORIGNAL ONE OFCOURSE"
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_PATH = os.path.join(app.root_path, "rwa.db")
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def create_table():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            photo TEXT,
            description TEXT,
            location TEXT,
            status TEXT DEFAULT 'Reported',
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


create_table()
def get_counts():
    conn = get_db()
    counts = {
        "reported": conn.execute("SELECT COUNT(*) FROM issues WHERE status = 'Reported'").fetchone()[0],
        "progress": conn.execute("SELECT COUNT(*) FROM issues WHERE status = 'In progress'").fetchone()[0],
        "resolved": conn.execute("SELECT COUNT(*) FROM issues WHERE status = 'Resolved'").fetchone()[0],
    }
    conn.close()
    counts["total"] = counts["reported"] + counts["progress"] + counts["resolved"]
    return counts


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "rwa_user" not in session:
            return redirect("/login")
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
  return render_template("rwa.html")
@app.route("/report")
def report():
  def report():
    if request.method == "POST":
        category = request.form["category"]
        description = request.form["description"]
        location = request.form["location"]

        photo = request.files["photo"]
        filename = datetime.now().strftime("%Y%m%d%H%M%S_") + secure_filename(photo.filename)
        photo.save(os.path.join(UPLOAD_FOLDER, filename))

        conn = get_db()
        conn.execute(
            "INSERT INTO issues (category, photo, description, location, created_at) VALUES (?, ?, ?, ?, ?)",
            (category, filename, description, location, datetime.now().strftime("%d %b %Y, %I:%M %p")),
        )
        conn.commit()
        conn.close()

        return redirect("/track")
  return render_template("rwa_report.html")
@app.route("/track")
def track():
    conn = get_db()
    issues = conn.execute("SELECT * FROM issues ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("rwa_track.html", issues=issues, counts=get_counts())
@app.route("/login", methods=["GET", "POST"])
def login():
    if "rwa_user" in session:
        return redirect("/dashboard")

    error = None
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["rwa_user"] = user["username"]
            session["rwa_name"] = user["full_name"]
            return redirect("/dashboard")
        error = "Wrong username or password."

    return render_template("rwa_login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
   
@app.route("/dashboard")
def dashboard():
  return render_template("rwa_dashboard.html")
  if __name__ == "__main__":
    app.run(debug=True)
@app.route("/update_status/<int:issue_id>", methods=["POST"])
@login_required
def update_status(issue_id):
    status = request.form["status"]
    if status in ("Reported", "In progress", "Resolved"):
        conn = get_db()
        conn.execute("UPDATE issues SET status = ? WHERE id = ?", (status, issue_id))
        conn.commit()
        conn.close()
    return redirect("/dashboard")


if __name__ == "__main__":
    app.run(debug=True)
