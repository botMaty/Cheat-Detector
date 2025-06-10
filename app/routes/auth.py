from flask import Blueprint, redirect, render_template, request, session, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['login_name']
        if len(name) > 2:
            session['name'] = name
            return render_template('prepare_quiz.html')
        else:
            return render_template('login.html')  # Error case
    else:
        if 'name' in session:
            session.pop('name')
        return render_template('login.html')