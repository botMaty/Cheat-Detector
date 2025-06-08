from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import json
import os

DATA_FILE = 'data.json'
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
            return render_template("prepare_quiz.html")
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

@app.route('/save/', methods=['POST'])
def save():
    if "name" not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 403

    name = session["name"]
    answers = request.get_json()

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = {}

    all_data[name] = answers

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    return jsonify({"status": "saved"})

@app.route('/end_quiz/')
def end_quiz():
    if "name" in session:
        session.pop("name")
        return render_template("end_quiz.html")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
