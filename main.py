import argparse
import os
import uuid

from flask import Flask, render_template, redirect, send_file, request
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm

from git_operations.valid import *
from git_operations.client_branch import ClientRepo


# console params
params = argparse.ArgumentParser()
params.add_argument('--heroku', action='store_true')
args = params.parse_args()

# app init
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key'


# client repo init
repo_name = "CLIENT_REPO"
main_path = os.path.dirname(os.path.realpath(__file__))
curr_dir = os.path.join(main_path, repo_name)
heroku_bot_git_url = 'https://github.com/MichaelShulga/bot-creator-heroku'
client_repo = ClientRepo(curr_dir, heroku_bot_git_url)

# update client settings folder
client_repo.update_client_settings()


# необходимая функция для работы сего модуля
# id -> объект User
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Регистрация - ничего не изменилось
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    print(print(form.validate_on_submit()))
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration', form=form,
                                   message="Password mismatch")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration', form=form,
                                   message="This user already exists")
        user = User(email=form.email.data)
        print(user)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Registration', form=form)


# Вход
# Предварительно нужно создать класс LoginForm и шаблон login.html
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Incorrect login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


# Выход из учетной записи
# 1. декоратор login_required можно добавлять ко всем функциям, где требуется быть авторизованным
# 2. функция не возвращает страницу, а совершает действие
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    return render_template('index.html')


# creating bot
@app.route('/vk_bot', methods=['POST', 'GET'])
def vk_bot():
    if request.method == 'GET':
        return render_template('vk_bot.html')
    elif request.method == 'POST':
        # bot.py
        f1 = request.files['file']

        # additional.json
        group_id, token = request.form.get('group_id'), request.form.get('token')
        additional = {"id": group_id, "token": token, "running": False, "errors": []}

        # not correct data input
        if not f1:
            return render_template('vk_bot.html', message='Choose file')
        if not is_python_file_valid(f1):
            return render_template('vk_bot.html', message='Invalid file')
        if is_file_damaged(f1, 'client_settings/bot.py'):
            return render_template('vk_bot.html', message='Damaged file')
        if not all([group_id, token]):
            return render_template('vk_bot.html', message='Missing token or id')
        if not is_correct_vk_id_and_token(group_id, token):
            return render_template('vk_bot.html', message='Invalid token or id')

        # create new client branch

        # update client files
        client_repo.update_bot_file(f1)
        client_repo.update_additional_file(additional)

        # commit_and_push
        branch = str(uuid.uuid4())
        repository, status = client_repo.commit_and_push(branch)

        details = {"REPOSITORY": repository, "STATUS": status}
        print(details)
        return render_template('deploy.html', repository=repository, details=details)


#  download bot.py file
@app.route('/download_file_vk_bot')
def download_file_vk_bot():
    path = "client_settings/bot.py"
    return send_file(path, as_attachment=True)


def main():
    # database initialization
    db_session.global_init("db/blogs.db")

    if args.heroku:  # run on heroku service
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)
    else:  # run on my pc
        app.run(port=8091, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
