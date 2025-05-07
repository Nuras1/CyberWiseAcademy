from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(nickname=nickname, email=email)
            db.session.add(user)
            db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('course'))
    return render_template('login.html')

@app.route('/course')
def course():
    return render_template('course.html')

@app.route('/submit_result', methods=['POST'])
def submit_result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    course_name = request.form['course_name']
    score = int(request.form['score'])
    user_id = session['user_id']
    new_result = Result(course_name=course_name, score=score, user_id=user_id)
    db.session.add(new_result)
    db.session.commit()
    return redirect(url_for('results'))

@app.route('/results')
def results():
    all_results = db.session.query(Result, User).join(User).all()
    return render_template('results.html', all_results=all_results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

