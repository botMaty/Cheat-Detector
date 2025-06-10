from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import json
import os
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer

DATA_FILE = 'data.json'
app = Flask(__name__)
CORS(app, resources={r"/cheat_detection": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]}})  # Allow specific origins
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
    try:
        with open('db.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({'error': 'No results data found'}), 404

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

    def calculate_percentages(answers_comparison, max_time_threshold=10):
        if not answers_comparison:
            return 0.0, []
        
        sbert_scores = []
        tfidf_scores = []
        diff_scores = []
        time_similarities = []
        question_percentages = []
        
        weights = {
            'sbert': 0.44,
            'tfidf': 0.23,
            'diff': 0.23,
            'time': 0.1
        }
        
        for comparison in answers_comparison:
            sbert_score = comparison['cosine_similarity_sbert']
            tfidf_score = comparison['cosine_similarity_tfidf']
            diff_score = comparison['diff_similarity']
            time_diff = comparison['time_difference']
            
            # Calculate time similarity
            time_similarity = 0
            if time_diff is not None:
                time_similarity = max(0, 1 - (time_diff / max_time_threshold))
            
            # Calculate question-specific percentage
            question_score = (
                weights['sbert'] * sbert_score +
                weights['tfidf'] * tfidf_score +
                weights['diff'] * diff_score +
                weights['time'] * time_similarity
            )
            question_percentage = round(question_score * 100, 2)
            question_percentages.append(question_percentage)
            
            # Collect scores for overall percentage
            sbert_scores.append(sbert_score)
            tfidf_scores.append(tfidf_score)
            diff_scores.append(diff_score)
            if time_diff is not None:
                time_similarities.append(time_similarity)
        
        # Calculate overall percentage
        avg_sbert = sum(sbert_scores) / len(sbert_scores) if sbert_scores else 0
        avg_tfidf = sum(tfidf_scores) / len(tfidf_scores) if tfidf_scores else 0
        avg_diff = sum(diff_scores) / len(diff_scores) if diff_scores else 0
        avg_time_similarity = sum(time_similarities) / len(time_similarities) if time_similarities else 0
        
        overall_score = (
            weights['sbert'] * avg_sbert +
            weights['tfidf'] * avg_tfidf +
            weights['diff'] * avg_diff +
            weights['time'] * avg_time_similarity
        )
        overall_percentage = round(overall_score * 100, 2)
        
        return overall_percentage, question_percentages

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

            # Calculate overall and question-specific percentages
            overall_percentage, question_percentages = calculate_percentages(pair_details)
            
            # Add question_percentage to each question in pair_details
            for idx, detail in enumerate(pair_details):
                detail['question_cheating_percentage'] = question_percentages[idx]

            pair_data = {
                'student1': student1,
                'student2': student2,
                'answers_comparison': pair_details,
                'overall_percentage': overall_percentage
            }
            all_pairs.append(pair_data)

    # Sort pairs by overall_percentage in descending order
    all_pairs.sort(key=lambda x: x['overall_percentage'], reverse=True)

    return jsonify({'pairs': all_pairs})


@app.route('/show_cheaters')
def show_cheaters():
    return render_template('cheaters.html')

if __name__ == '__main__':
    app.run(debug=True)
