from flask import Flask, render_template, request, redirect, make_response, session, abort, jsonify
# from flask_ngrok import run_with_ngrok
# from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
db_session.global_init("db/tests.sqlite")

from data.__all_models import *
# from forms.__all_forms import *

import datetime
import os


app = Flask(__name__)
# login_manager = LoginManager()
# login_manager.init_app(app)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'testing_system_key'


def main():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='127.0.0.1', port=port)
    # app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

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


@app.route("/")
@app.route("/index")
def index():
    return "<b>HELL</b>o world"


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