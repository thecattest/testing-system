from flask import Flask, render_template, request, redirect, make_response, session, abort, jsonify
from flask_ngrok import run_with_ngrok
# from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
db_session.global_init("db/tests.sqlite")

from data.__all_models import *
# from forms.__all_forms import *

import datetime
import random
import os


app = Flask(__name__)
# login_manager = LoginManager()
# login_manager.init_app(app)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'testing_system_key'
# app.config['DEBUG'] = 'OFF'


def fill_db():
    session = db_session.create_session()
    test = Test()
    test.name = "Arithmetic"
    test.description = "The simplest questions for testing"
    session.add(test)

    questions = [
        {
            "text": "2 + 2",
            "answers": [
                {"text": "14", "is_correct": False},
                {"text": "8", "is_correct": False},
                {"text": "4", "is_correct": True},
                {"text": "16 ", "is_correct": False}
            ]
        },
        {
            "text": "14 + 20",
            "answers": [
                {"text": "32", "is_correct": False},
                {"text": "34", "is_correct": True},
                {"text": "24", "is_correct": False},
                {"text": "16 ", "is_correct": False}
            ]
        },
        {
            "text": "10 - 8",
            "answers": [
                {"text": "2", "is_correct": True},
                {"text": "8", "is_correct": False},
                {"text": "4", "is_correct": False},
                {"text": "16 ", "is_correct": False}
            ]
        }
    ]

    for q in questions:
        question = Question()
        question.text = q["text"]
        question.test = test
        session.add(question)
        for a in q["answers"]:
            answer = Answer()
            answer.text = a["text"]
            answer.is_correct = a["is_correct"]
            answer.question = question
            session.add(answer)
    session.commit()


def main():
    # fill_db()
    port = int(os.environ.get("PORT", 8000))
    app.run(host='127.0.0.1', port=port)
    # app.run()

'''
@app.errorhandler(404)
def not_found(error):
    return render_template("error_404.html")


@app.errorhandler(403)
def not_found(error):
    return render_template("error_403.html")
'''
'''
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)
    

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("login.html",
                               title='Log in',
                               message="Password or login is incorrect",
                               form=form)
    return render_template('login.html', title='Log in', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
'''

def log(error):
    message = str(type(error)) + ": " + str(error)
    with open('log.txt', 'a') as file:
        file.write(message + '\n' + str(datetime.datetime.now()) + '\n-----\n')


def test_started():
    db = db_session.create_session()
    if db.query(Result).filter(Result.is_finished == False).first():
        return True
    return False


@app.route("/")
@app.route("/index")
@app.route("/all_tests")
def index():
    if test_started():
        return redirect('/test')
    db = db_session.create_session()
    tests = db.query(Test).all()
    return render_template("all_tests.html",
                           title="Тесты",
                           tests=tests)


@app.route("/tests/<int:test_id>")
def start_test(test_id):
    if test_started():
        return redirect('/test')
    db = db_session.create_session()
    test = db.query(Test).get(test_id)
    if not test:
        return render_template("error.html",
                               text="Произошла ошибка. Скорее всего, тест не существует или был удалён.",
                               button="На главную",
                               link="/all_tests")
    result = Result()
    result.name = test.name
    db.add(result)
    for q in test.questions:
        row = ResultRow()
        row.result = result
        row.text = q.text
        row.q_id = q.id
        for a in q.answers:
            if a.is_correct:
                row.correct = a.text
                break
        db.add(row)
    db.commit()
    return redirect("/test")


@app.route("/test")
def test():
    if not test_started():
        return redirect("/all_tests")
    db = db_session.create_session()
    result = db.query(Result).filter(Result.is_finished == False).first()
    questions = db.query(ResultRow).filter(ResultRow.result_id == result.id).all()
    questions = list(q for q in questions if q.answer is None)
    if questions:
        q_id = random.choice(questions).q_id
        question = db.query(Question).get(q_id)
        if question:
            return render_template("question.html",
                                   title=result.name,
                                   question=question)
        return render_template("error.html",
                               text="Произошла ошибка. Скорее всего, тест был удалён.",
                               button="На главную",
                               link="/finish_test")
    return redirect("/finish_test")


@app.route("/save_answer", methods=["GET", "POST"])
def save_answer():
    try:
        q_id = request.form["question_id"]
        answer = request.form["answer"]
    except KeyError:
        return redirect('/test')
    db = db_session.create_session()
    result = db.query(Result).filter(Result.is_finished == False).first()
    question = db.query(ResultRow).filter(ResultRow.result == result,
                                              ResultRow.q_id == q_id).first()
    if not question:
        return redirect('/test')
    question.answer = answer
    db.commit()
    return redirect('/test')


@app.route("/finish_test")
def finish_test():
    if not test_started():
        return redirect("/all_tests")
    db = db_session.create_session()
    st = db.query(Result).filter(Result.is_finished == False).first()
    st.is_finished = True
    db.commit()
    return redirect("/all_tests")


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/session_test')
def session_test():
    if 'visits_count' in session:
        session['visits_count'] = session.get('visits_count') + 1
    else:
        session['visits_count'] = 1
    return f"Вы пришли на эту страницу {session['visits_count']} раз"


if __name__ == '__main__':
    main()