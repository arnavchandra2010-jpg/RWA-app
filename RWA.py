from flask import flask , render_templates
app = flask(__name__)
@app.route("/")
def home():
  return render_template("rwa.html")
@app.route("/report")
def report():
  return render_template("rwa_report.html")
@app.route("/tracker")
def tracker():
  return render_template("rwa_tracker.html")
@app.route("/dashboard")
def dashboard():
  return render_template("rwa_dashboard.html")
  if __name__ == "__main__":
    app.run(debug=True)
