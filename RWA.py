from flask import flask , render_templates
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = flask(__name__)
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
@app.route("/tracker")
def tracker():
   conn = get_db()
    issues = conn.execute("SELECT * FROM issues ORDER BY id DESC").fetchall()
    counts = {
        "reported": conn.execute("SELECT COUNT(*) FROM issues WHERE status = 'Reported'").fetchone()[0],
        "progress": conn.execute("SELECT COUNT(*) FROM issues WHERE status = 'In progress'").fetchone()[0],
        "resolved": conn.execute("SELECT COUNT(*) FROM issues WHERE status = 'Resolved'").fetchone()[0],
    }
    conn.close()
    return render_template("rwa_track.html", issues=issues, counts=counts)

  return render_template("rwa_tracker.html")
@app.route("/dashboard")
def dashboard():
  return render_template("rwa_dashboard.html")
  if __name__ == "__main__":
    app.run(debug=True)
