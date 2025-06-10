from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer

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

# --- Load JSON "DB" ---
def load_data():
    with open('db.json', 'r') as f:
        return json.load(f)

@app.route('/cheat_detection')
def cheat_detection():

    data = load_data()

    students = list(data.keys())
    if len(students) < 2:
        return jsonify({'error': 'Not enough submissions to analyze'}), 400

    def get_latest_answer(student_answers, qnum):
        matches = [a for a in student_answers if a['qnumber'] == qnum]
        return matches[-1] if matches else None

    question_numbers = sorted(set(q['qnumber'] for student in data for q in data[student]))
    answers = {qnum: {student: get_latest_answer(data[student], qnum)['description']
                     for student in students
                     if get_latest_answer(data[student], qnum)}
              for qnum in question_numbers}
    times = {qnum: {student: get_latest_answer(data[student], qnum)['time_taken']
                   for student in students
                   if get_latest_answer(data[student], qnum)}
            for qnum in question_numbers}

    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1,3), stop_words='english')

    all_pairs = []
    for i in range(len(students)):
        for j in range(i + 1, len(students)):
            student1, student2 = students[i], students[j]
            pair_details = []

            for qnum in question_numbers:
                ans1 = str(answers[qnum][student1]).strip()
                ans2 = str(answers[qnum][student2]).strip()

                matcher = SequenceMatcher(None, ans1, ans2)
                matching_blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
                total_match_len = sum(b.size for b in matching_blocks)
                diff_similarity = total_match_len / max(len(ans1), len(ans2)) if max(len(ans1), len(ans2)) > 0 else 0

                try:
                    tfidf_matrix = tfidf_vectorizer.fit_transform([ans1, ans2])
                    cosine_sim_tfidf = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                except Exception:
                    cosine_sim_tfidf = 0

                try:
                    embeddings = sbert_model.encode([ans1, ans2])
                    cosine_sim_sbert = cosine_similarity(
                        embeddings[0].reshape(1, -1),
                        embeddings[1].reshape(1, -1)
                    )[0][0]
                except Exception:
                    cosine_sim_sbert = 0

                time_diff = abs(times[qnum][student1] - times[qnum][student2]) if (student1 in times[qnum] and student2 in times[qnum]) else None

                pair_details.append({
                    'qnumber': qnum,
                    'answer1': ans1,
                    'answer2': ans2,
                    'diff_similarity': float(round(diff_similarity, 4)),
                    'cosine_similarity_tfidf': float(round(cosine_sim_tfidf, 4)),
                    'cosine_similarity_sbert': float(round(cosine_sim_sbert, 4)),
                    'time_difference': time_diff
                })

            all_pairs.append({
                'student1': student1,
                'student2': student2,
                'answers_comparison': pair_details
            })

    return jsonify({'pairs': all_pairs})

if __name__ == '__main__':
    app.run(debug=True)
