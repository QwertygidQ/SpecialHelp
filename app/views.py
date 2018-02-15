from . import app, db
from .models import User, ROLE_USER
from .forms import SignInForm, SignUpForm
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from functools import wraps


def role_required(role=ROLE_USER):
    def wrapper(func):
        @wraps(func)
        def role_checker(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)

            if role == ROLE_USER or current_user.role == role:
                return func(*args, **kwargs)
            else:
                abort(403)

        return role_checker
    return wrapper



@app.route('/')
def index():
    return render_template('index.html',
                           title='Main Page')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember.data)

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')

            return redirect(next_page)
        else:
            flash('Неверный Email или пароль')

    return render_template('signin.html',
                           title='Sign in',
                           form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('signup.html',
                           title='Sign up',
                           form=form)

@app.route('/signout')
def signout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('index')) # redirect to next TODO??
    else:
        abort(401)