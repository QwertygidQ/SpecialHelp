from . import app, db
from .models import User, ROLE_USER
from .forms import SignInForm, SignUpForm, UserUpdateForm, ProfileUpdateForm
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


def is_safe(url):
    return url and url_parse(url).netloc == ''


def get_next_page(default='index'):
    pages = [request.args.get('next'), request.referrer]
    for page in pages:
        if is_safe(page):
            return page

    return url_for(default)


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
            return redirect(get_next_page(default='index'))
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
        return redirect(get_next_page(default='index'))
    else:
        abort(401)


@app.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)

    return render_template('profile.html',
                           title='Профиль пользователя {}'.format(username),
                           user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    userform = UserUpdateForm()
    profileform = ProfileUpdateForm()

    if userform.user_update_submit.data and userform.validate_on_submit():
        if current_user.check_password(userform.current_password.data):
            if userform.email.data != '':
                current_user.email = userform.email.data

            if userform.username.data != '':
                current_user.username = userform.username.data

            if userform.password.data != '':
                current_user.set_password(userform.password.data)

            db.session.commit()

            return redirect(url_for('profile', username=current_user.username))
        else:
            flash('Неверный текущий пароль')
    elif profileform.profile_update_submit.data and profileform.validate_on_submit():
        if current_user.check_password(userform.current_password.data):
            if profileform.about != '':
                current_user.about = profileform.about.data

            if profileform.contacts != '':
                current_user.contacts = profileform.contacts.data

            db.session.commit()

            return redirect(url_for('profile', username=current_user.username))
        else:
            flash('Неверный текущий пароль')

    return render_template('edit_profile.html',
                           userform=userform,
                           profileform=profileform,
                           user=current_user)
