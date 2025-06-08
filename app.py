from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "1234"

@app.route("/")
def home():
    return redirect(url_for("login"))
    
@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form["login_name"]
        if len(name) > 2:
            session["name"] = name
            return redirect(url_for("login"))
        else:
            return render_template("login.html") # error
    else:
        if "name" in session:
            session.pop("name")
        return render_template("login.html")
        
@app.route("/quiz/")
def quiz():
    if "name" not in session:
        return redirect(url_for("login"))
    return render_template("quiz.html")
