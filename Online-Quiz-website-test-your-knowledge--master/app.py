import os
from flask import Flask, request, redirect, render_template, send_from_directory, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Нужно для сессии!

basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    quiz_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Такой email уже зарегистрирован!"

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username  # Сохраняем в сессию
        return redirect('/index.html')
    return render_template('register.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    score = int(request.form['score'])
    username = session.get('username', 'Аноним')  # Если не нашли в сессии — "Аноним"
    quiz_name = "CyberWise Scenario Quiz"

    result = QuizResult(username=username, quiz_name=quiz_name, score=score)
    db.session.add(result)
    db.session.commit()
    return redirect('/results')

@app.route('/results')
def results():
    results_list = QuizResult.query.all()
    return render_template('results.html', results=results_list)

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(basedir, filename)

if __name__ == '__main__':
    app.run(debug=True)
