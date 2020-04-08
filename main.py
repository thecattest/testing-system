from flask import Flask, render_template, request, redirect, make_response, session, abort, jsonify
from flask_ngrok import run_with_ngrok
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
import sqlalchemy as sa
db_session.global_init("db/tests.sqlite")

from data.__all_models import *
from forms.__all_forms import *

import datetime
import random
import os


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.unauthorized_handler(callback=(lambda: redirect('/login')))
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'testing_system_key'
# app.config['DEBUG'] = 'OFF'


def fill_db():
    session = db_session.create_session()

    test = Test()
    test.name = "Arithmetic 1"
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

    test = Test()
    test.name = "Arithmetic 2"
    test.description = "A bit harder questions for testing"
    session.add(test)

    questions = [
        {
            "text": "14 - 5",
            "answers": [
                {"text": "14", "is_correct": False},
                {"text": "8", "is_correct": False},
                {"text": "11", "is_correct": True},
                {"text": "16 ", "is_correct": False}
            ]
        },
        {
            "text": "23 + 0",
            "answers": [
                {"text": "32", "is_correct": False},
                {"text": "23", "is_correct": True},
                {"text": "24", "is_correct": False},
                {"text": "16 ", "is_correct": False}
            ]
        },
        {
            "text": "5 + 7",
            "answers": [
                {"text": "12", "is_correct": True},
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


def add_type(name):
    session = db_session.create_session()
    type = UserType()
    type.name = name
    session.add(type)
    session.commit()


def main():
    '''
    fill_db()

    add_type('Администратор')
    add_type('Учитель')
    add_type('Ученик')

    add_user('ilya-vodopyanov', 'password', 1)

    add_user('teacher', 'password', 2)

    add_user('student1', 'password', 3)
    add_user('student2', 'password', 3)
    add_user('student3', 'password', 3)
    '''
    port = int(os.environ.get("PORT", 8000))
    app.run(host='127.0.0.1', port=port)
    # app.run()


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def log(error):
    message = str(type(error)) + ": " + str(error)
    with open('log.txt', 'a') as file:
        file.write(message + '\n' + str(datetime.datetime.now()) + '\n-----\n')


def test_started():
    db = db_session.create_session()
    if db.query(Result).filter(Result.is_finished == False, Result.user == current_user).first():
        return True
    return False


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.nickname == form.nickname.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/more")
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


@app.route("/")
@app.route("/index")
@app.route("/all_tests")
@login_required
def index():
    if test_started():
        return redirect('/test')
    db = db_session.create_session()
    tests = db.query(Test).all()
    return render_template("all_tests.html",
                           title="Тесты",
                           tests=tests,
                           all_tests='active')


@app.route("/groups")
@login_required
def get_groups():
    code = 0
    db = db_session.create_session()
    groups = db.query(Group).all()
    if current_user.type_id == 3:
        groups = list(group for group in groups if current_user in group.users)
    if not groups:
        code = 1
    return render_template("all_groups.html",
                           title='Группы',
                           groups=groups,
                           code=code)


@app.route("/groups/<int:group_id>")
@login_required
def get_group(group_id):
    code = 0
    db = db_session.create_session()
    group = db.query(Group).get(group_id)
    users = []
    if not group:
        code = 1
    elif current_user.type_id != 1 and current_user != group.creator:
        code = 2
    else:
        users = db.query(User).filter(User.type_id != 1,
                                      User != current_user).order_by(User.type_id).all()
        users = list(user for user in users if not user in group.users and user != group.creator)
    return render_template("group.html",
                           title='Редактирование',
                           group=group,
                           users=users,
                           code=code)


@app.route("/create_group", methods=['GET', 'POST'])
@login_required
def create_group():
    if current_user.type_id != 3:
        form = CreateGroupForm()
        if form.validate_on_submit():
            name = form.name.data
            db = db_session.create_session()
            group = Group()
            group.creator_id = current_user.id
            group.name = name
            db.add(group)
            db.commit()
            return redirect(f'/groups/{group.id}')
        return render_template("create_group.html",
                               form=form)
    else:
        return redirect('/more')


@app.route('/remove_user/<int:user_id>/<int:group_id>')
@login_required
def remove_user(user_id, group_id):
    db = db_session.create_session()
    user = db.query(User).get(user_id)
    group = db.query(Group).get(group_id)
    if user and group and user in group.users and (current_user.type_id == 1 or group.creator == current_user):
        group.users.remove(user)
        db.commit()
    return redirect(f'/groups/{group_id}')


@app.route('/add_user/<int:user_id>/<int:group_id>')
@login_required
def add_user(user_id, group_id):
    db = db_session.create_session()
    group = db.query(Group).get(group_id)
    if group and (current_user.type_id == 1 or current_user == group.creator):
        user = db.query(User).get(user_id)
        if not user:
            return
        group.users.append(user)
        db.commit()
    return redirect(f'/groups/{group_id}')


@app.route("/register", methods=['GET', 'POST'])
@login_required
def create_user():
    code = 0
    form = RegisterForm()
    if current_user.type_id == 3:
        code = 1
    else:
        if form.validate_on_submit():
            db = db_session.create_session()
            user = User()
            user.nickname = form.nickname.data
            user.creator_id = current_user.id
            user.set_password(form.password.data)
            if form.is_teacher.data:
                user.type_id = 2
            else:
                user.type_id = 3
            db.add(user)
            db.commit()
            return redirect('/users')
    return render_template('register.html', title='Создать', form=form, code=code)


@app.route("/statistics/<int:test_id>")
@login_required
def get_test_statistics(test_id):
    db = db_session.create_session()
    if current_user.type_id == 3:
        results = db.query(Result).filter(Result.test_id == test_id,
                                          Result.user_id == current_user.id,
                                          ~Result.is_deleted).all()
    else:
        results = db.query(Result).filter(Result.test_id == test_id).all()
    results.reverse()
    return show_statistics(results)


@app.route("/user_statistics/<int:user_id>")
@login_required
def get_user_statistics(user_id):
    code = 0
    if user_id != current_user.id and current_user.type_id == 3:
        code = 2
        results = []
    else:
        db = db_session.create_session()
        if current_user.type_id == 3:
            results = db.query(Result).filter(Result.user_id == user_id, ~Result.is_deleted).all()
        else:
            results = db.query(Result).filter(Result.user_id == user_id).all()
    results.reverse()
    return show_statistics(results, code=code)


@app.route("/statistics")
@login_required
def get_statistics():
    db = db_session.create_session()
    results = db.query(Result).filter(Result.user_id == current_user.id, ~Result.is_deleted).all()
    results.reverse()
    return show_statistics(results)


def show_statistics(results, code=0):
    if not results and code == 0:
        code = 1
    for r in results:
        all_answers = list(a.answer == a.correct for a in r.rows)
        r.n_correct_answers = all_answers.count(True)
        r.n_all_answers = len(all_answers)
        r.finish_date = datetime.datetime.strftime(r.end_date, "%d %b, %H:%M")
    return render_template("statistics.html",
                           title="История",
                           results=results,
                           code=code,
                           statistics='active')


@app.route('/users')
@login_required
def get_users():
    try:
        code = 0
        if current_user.type_id == 3:
            code = 1
        db = db_session.create_session()
        users = db.query(User).order_by(User.type_id).all()
        return render_template('users.html',
                               title='Пользователи',
                               users=users,
                               code=code)
    except sa.orm.exc.DetachedInstanceError:
        return redirect('/users')


@app.route("/delete_result/<int:result_id>")
@login_required
def delete_result(result_id):
    db = db_session.create_session()
    result = db.query(Result).get(result_id)
    if not result or (not result.user == current_user and current_user.type_id != 1):
        return redirect('/statistics')
    result.is_deleted = True
    db.commit()
    return redirect(f'/statistics/{result.test_id}')


@app.route('/delete_group/<int:group_id>')
@login_required
def delete_group(group_id):
    db = db_session.create_session()
    group = db.query(Group).get(group_id)
    if group and (group.creator == current_user or current_user.type_id == 1):
        group.users = []
        db.delete(group)
        db.commit()
    return redirect('/groups')


@app.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    db = db_session.create_session()
    user = db.query(User).get(user_id)
    if user and user in current_user.created or current_user.type_id == 1:
        for group in user.created_groups:
            delete_group(group.id)
        db.delete(user)
        db.commit()
    return redirect('/users')


@app.route("/test/<int:test_id>")
@login_required
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
    result.test_id = test.id
    result.user_id = current_user.id
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
@login_required
def test():
    if not test_started():
        return redirect("/all_tests")
    db = db_session.create_session()
    result = db.query(Result).filter(Result.is_finished == False).first()
    questions = db.query(ResultRow).filter(ResultRow.result_id == result.id).all()
    result.n_questions = len(questions)
    questions = list(q for q in questions if q.answer is None)
    result.current_n = result.n_questions - len(questions) + 1
    if questions:
        q_id = random.choice(questions).q_id
        question = db.query(Question).get(q_id)
        question.n_questions = result.n_questions
        question.current_n = result.current_n
        if question:
            return render_template("question.html",
                                   title=result.test.name,
                                   question=question,
                                   all_tests="active")
        return render_template("error.html",
                               text="Произошла ошибка. Скорее всего, тест был удалён.",
                               button="На главную",
                               link="/finish_test")
    return redirect("/finish_test")


@app.route("/save_answer", methods=["GET", "POST"])
@login_required
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
@login_required
def finish_test():
    if not test_started():
        return redirect("/all_tests")
    db = db_session.create_session()
    st = db.query(Result).filter(Result.is_finished == False).first()
    if all(list(i.answer == None for i in st.rows)):
        db.delete(st)
        db.commit()
        return redirect('/all_tests')
    st.is_finished = True
    st.end_date = datetime.datetime.now()
    db.commit()
    return redirect("/statistics/{}".format(st.test_id))


@app.route('/more')
@login_required
def more():
    try:
        return render_template('more.html',
                               title='Дополнительно',
                               more='active')
    except sa.orm.exc.DetachedInstanceError:
        return redirect('/more')


if __name__ == '__main__':
    main()