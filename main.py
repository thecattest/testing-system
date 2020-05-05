from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
import sqlalchemy as sa
import os

try:
    db_session.global_init(os.path.join(os.getcwd(), "db", "tests.sqlite"))
except sa.exc.OperationalError:
    db_session.global_init("/home/ilyav/testing-system/db/tests.sqlite")

from data.__all_models import *
from forms.__all_forms import *

from notifications import bot

import datetime
import random

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.unauthorized_handler(callback=(lambda: redirect('/login')))
app.config['SECRET_KEY'] = 'testing_system_key'


def del_test(test_id):
    db = db_session.create_session()
    test = db.query(Test).get(test_id)
    if test:
        for q in test.questions:
            for a in q.answers:
                db.delete(a)
            db.delete(q)
        db.delete(test)
    db.commit()


def main():
    # del_test(3)
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=8000)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    session.expire_on_commit = False
    return session.query(User).get(user_id)


def log(error):
    message = str(type(error)) + ": " + str(error)
    with open('log.txt', 'a') as file:
        file.write(message + '\n' + str(datetime.datetime.now()) + '\n-----\n')


def is_allowed(test, user):
    return any(list(group.id in list(i.id for i in test.groups)
                    for group in user.groups)) \
           or test.creator == current_user \
           or current_user.type_id == 1


def test_started():
    db = db_session.create_session()
    if db.query(Result).filter(~Result.is_finished, Result.user == current_user).first():
        return True
    return False


def add_group_to_test(group_id, test_id):
    db = db_session.create_session()
    group = db.query(Group).get(group_id)
    test = db.query(Test).get(test_id)
    if group and test and (current_user.type_id == 1 or current_user == test.creator):
        test.groups.append(group)
        for user in group.users:
            notif = Notification()
            notif.user_id = user.id
            notif.text = f"Вам открыли доступ к тесту {test.name}"
            notif.link = "/"
            db.add(notif)
        db.commit()


def remove_group_from_test(group_id, test_id):
    db = db_session.create_session()
    group = db.query(Group).get(group_id)
    test = db.query(Test).get(test_id)
    if group and test and group in test.groups and (current_user.type_id == 1 or current_user == test.creator):
        test.groups.remove(group)
        for user in group.users:
            notif = Notification()
            notif.user_id = user.id
            notif.text = f"У вас больше нет доступа к тесту {test.name}"
            notif.link = "/"
            db.add(notif)
        db.commit()


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.nickname == form.nickname.data.strip().lower()).first()
        if user and user.check_password(form.password.data.strip()):
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


# @app.route("/check")
@login_required
def check():
    db = db_session.create_session()
    bot.check_updates(db, User)
    return "Ok"


# @app.route('/notify/<text>')
def notify_users(text):
    db = db_session.create_session()
    users = db.query(User).all()
    bot.notify(users, text)
    return "Ok"


@app.route("/")
@app.route("/index")
@app.route("/all_tests")
@login_required
def index():
    try:
        if test_started():
            return redirect('/test')
        db = db_session.create_session()
        tests = db.query(Test).all()
        tests = list(test for test in tests if is_allowed(test, current_user))
        return render_template("all_tests.html",
                               title="Тесты",
                               tests=tests,
                               all_tests='active')
    except sa.orm.exc.DetachedInstanceError:
        return redirect('/')


@app.route("/groups")
@login_required
def get_groups():
    try:
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
                               other="/groups",
                               other_title='Группы',
                               code=code)
    except sa.orm.exc.DetachedInstanceError:
        return redirect("/groups")


@app.route("/groups/<int:group_id>")
@login_required
def get_group(group_id):
    try:
        code = 0
        edit = True
        title = 'Редактирование'
        db = db_session.create_session()
        group = db.query(Group).get(group_id)
        tests = []
        users = []
        if not group:
            code = 1
        elif current_user.type_id == 3:
            code = 2
        else:
            if current_user.type_id != 1 and current_user != group.creator:
                edit = False
                title = 'Просмотр'
            tests = db.query(Test).all()
            tests = list(filter(lambda t: group not in t.groups, tests))
            if current_user.type_id == 2:
                tests = list(filter(lambda t: t.creator == current_user, tests))
            users = db.query(User).filter(User.type_id != 1,
                                          User != current_user).order_by(User.type_id).all()
            users = list(user for user in users if not user in group.users and user != group.creator)
        return render_template("group.html",
                               title=title,
                               group=group,
                               other="/groups",
                               other_title='Группы',
                               users=users,
                               tests=tests,
                               edit=edit,
                               code=code)
    except sa.orm.exc.DetachedInstanceError:
        return redirect(f"/groups/{group_id}")


@app.route('/test_to_groups/<int:test_id>')
def show_test_to_groups(test_id):
    code = 0
    groups = []
    edit = False
    db = db_session.create_session()
    test = db.query(Test).get(test_id)
    if not test:
        code = 1
    elif not is_allowed(test, current_user) and current_user.type_id != 1 or current_user.type_id == 3:
        code = 2
    else:
        groups = db.query(Group).filter(~Group.id.in_(list(group.id for group in test.groups))).all()
        edit = test.creator == current_user or current_user.type_id == 1
    return render_template("test_to_groups.html",
                           title="Группы с доступом",
                           test=test,
                           edit=edit,
                           groups=groups,
                           other=f"/test_to_groups/{test_id}",
                           other_title="Доступ",
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
                               other="/groups",
                               other_title='Группы',
                               form=form)
    else:
        return redirect('/more')


@app.route("/add_group_to_test/<int:test_id>/<int:group_id>")
@login_required
def add_group(test_id, group_id):
    add_group_to_test(group_id, test_id)
    return redirect(f'/test_to_groups/{test_id}')


@app.route("/remove_group_from_test/<int:test_id>/<int:group_id>")
@login_required
def remove_group(test_id, group_id):
    remove_group_from_test(group_id, test_id)
    return redirect(f'/test_to_groups/{test_id}')


@app.route("/add_test_to_group/<int:test_id>/<int:group_id>")
@login_required
def add_test(test_id, group_id):
    add_group_to_test(group_id, test_id)
    return redirect(f'/groups/{group_id}')


@app.route("/remove_test_from_group/<int:test_id>/<int:group_id>")
@login_required
def remove_test(test_id, group_id):
    remove_group_from_test(group_id, test_id)
    return redirect(f'/groups/{group_id}')


@app.route('/remove_user/<int:user_id>/<int:group_id>')
@login_required
def remove_user(user_id, group_id):
    db = db_session.create_session()
    user = db.query(User).get(user_id)
    group = db.query(Group).get(group_id)
    if user and group and user in group.users and (current_user.type_id == 1 or group.creator == current_user):
        group.users.remove(user)
        notif = Notification()
        notif.user_id = user.id
        notif.text = f"Вас удалили из группы {group.name} ({group.creator.nickname})"
        notif.link = "/groups"
        db.add(notif)
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
        notif = Notification()
        notif.user_id = user.id
        notif.text = f"Вас добавили в группу {group.name} ({group.creator.nickname})"
        notif.link = "/groups"
        db.add(notif)
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
            user.nickname = form.nickname.data.strip().lower()
            user.creator_id = current_user.id
            user.set_password(form.password.data.strip())
            if form.is_teacher.data:
                user.type_id = 2
            else:
                user.type_id = 3
            user.set_secret_code()
            db.add(user)
            db.commit()
            return redirect('/users')
    return render_template('register.html',
                           title='Создать',
                           form=form,
                           other="/register",
                           other_title='Регистрация',
                           code=code)


@app.route("/statistics/<int:test_id>")
@login_required
def get_test_statistics(test_id):
    try:
        code = 0
        results = []
        db = db_session.create_session()
        test = db.query(Test).get(test_id)
        if not test:
            code = 1
            return show_statistics(results, title=f"Такого теста нет", code=code)
        elif test.creator != current_user:
            results = db.query(Result).filter(Result.test_id == test_id,
                                              Result.user_id == current_user.id,
                                              ~Result.is_deleted).all()
        elif current_user.type_id == 1 or test.creator == current_user:
            results = db.query(Result).filter(Result.test_id == test_id).all()
        else:
            code = 2
        results.reverse()
        return show_statistics(results, title=f"История по {test.name}", code=code)
    except sa.orm.exc.DetachedInstanceError:
        return redirect(f"/statistics/{test_id}")


@app.route("/user_statistics/<int:user_id>")
@login_required
def get_user_statistics(user_id):
    try:
        if user_id == current_user.id:
            return redirect("/statistics")
        code = 0
        results = []
        nickname = ""
        db = db_session.create_session()
        user = db.query(User).get(user_id)
        if not user:
            code = 3
        elif (current_user.type_id == 3 and user != current_user) or \
                (current_user.type_id == 2 and user not in current_user.created and current_user != user):
            code = 2
        else:
            nickname = user.nickname
            if current_user.type_id == 3:
                results = db.query(Result).filter(Result.user_id == user_id, ~Result.is_deleted).all()
            else:
                results = db.query(Result).filter(Result.user_id == user_id).all()
        results.reverse()
        return show_statistics(results, title=f"История {nickname}", code=code)
    except sa.orm.exc.DetachedInstanceError:
        return redirect(f"/user_statistics/{user_id}")


@app.route("/statistics")
@login_required
def get_statistics():
    try:
        db = db_session.create_session()
        results = db.query(Result).filter(Result.user_id == current_user.id, ~Result.is_deleted).all()
        results.reverse()
        return show_statistics(results, title="Моя история")
    except sa.orm.exc.DetachedInstanceError:
        return redirect("/statistics")


def show_statistics(results, title, code=0):
    if not results and code == 0:
        code = 1
    for r in results:
        all_answers = list(a.answer == a.correct for a in r.rows)
        r.n_correct_answers = all_answers.count(True)
        r.n_all_answers = len(all_answers)
        r.finish_date = datetime.datetime.strftime(r.end_date, "%d %b, %H:%M")
    return render_template("statistics.html",
                           title=title,
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
                               other="/users",
                               other_title='Пользователи',
                               code=code)
    except sa.orm.exc.DetachedInstanceError:
        return redirect('/users')


@app.route("/delete_result/<int:result_id>")
@login_required
def delete_result(result_id):
    return render_template("error.html",
                           text="Теперь так нельзя.",
                           link="/statistics",
                           button="Вернуться",
                           other="/statistics",
                           other_title="Статистика")
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
        group.tests = []
        db.delete(group)
        db.commit()
    return redirect('/groups')


@app.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    try:
        db = db_session.create_session()
        user = db.query(User).get(user_id)
        if user and user in current_user.created or current_user.type_id == 1:
            if not user.created_groups:
                db.delete(user)
                db.commit()
            else:
                return render_template("error.html",
                                       text=f"Вы не можете удалить пользователя {user.nickname}, "
                                            "так как он является администратором одной или нескольких групп",
                                       link="/users",
                                       button="Вернуться")
            if user.results:
                user.results = []
            if user.groups:
                user.groups = []
        return redirect('/users')
    except sa.orm.exc.DetachedInstanceError:
        return redirect(f'/delete_user/{user_id}')


@app.route("/test/<int:test_id>")
@login_required
def start_test(test_id):
    try:
        if test_started():
            return redirect('/test')
        db = db_session.create_session()
        test = db.query(Test).get(test_id)
        if not test or not is_allowed(test, current_user):
            return render_template("error.html",
                                   text="Теста не существует или у вас нет прав доступа.",
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
    except sa.orm.exc.DetachedInstanceError:
        return redirect(f'/test/{test_id}')


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
    return redirect(f"/statistics/{st.test_id}".format(st.test_id))


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
