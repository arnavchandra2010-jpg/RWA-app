from flask import flask , render_templates
app = flask(__name__)
@app.route("/")
def home():
return render_template("rwa.html")
