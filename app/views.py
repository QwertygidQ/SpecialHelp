from . import app, db, email
from .models import User, Business
from .forms import SignInForm, SignUpForm, UserUpdateForm, ProfileUpdateForm, PasswordResetForm, NewPasswordForm
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
from werkzeug.urls import url_parse
from functools import wraps


# ======================= Decorators/helper functions =======================

def unauthenticated_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return f(*args, **kwargs)
        return redirect(url_for('index'))

    return wrapper


def is_safe(url):
    return url and url_parse(url).netloc == ''


def get_next_page(default='index'):
    pages = [request.args.get('next'), request.referrer]
    for page in pages:
        if is_safe(page):
            return page

    return url_for(default)


# ======================= View functions =======================

@app.route('/')
def index():
    return render_template('index.html',
                           title='Главная Страница')


@app.route('/signin', methods=['GET', 'POST'])
@unauthenticated_required
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == form.email.data.lower()).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember.data)
            return redirect(get_next_page())
        else:
            flash('Неверный Email или пароль')

    return render_template('signin.html',
                           title='Вход',
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
                           title='Регистрация',
                           form=form)


@app.route('/signout')
def signout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(get_next_page())
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
            if profileform.about.data != '':
                current_user.about = profileform.about.data

            if profileform.contacts.data != '':
                current_user.contacts = profileform.contacts.data

            db.session.commit()

            return redirect(url_for('profile', username=current_user.username))
        else:
            flash('Неверный текущий пароль')

    return render_template('edit_profile.html',
                           title='Изменение настроек профиля',
                           userform=userform,
                           profileform=profileform,
                           user=current_user)


@app.route('/reset_password', methods=['GET', 'POST'])
@unauthenticated_required
def reset_password():
    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == form.email.data.lower()).first()
        if user is not None:
            email.send_reset_password_email(user)
            flash('Письмо с ссылкой для сброса пароля было отправлено Вам на почту')

            return redirect(url_for('signin'))
        else:
            flash('Пользователя с таким Email не существует')

    return render_template('reset_password.html',
                           title='Сброс пароля',
                           form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
@unauthenticated_required
def reset_password_confirmed(token):
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('signin'))

    form = NewPasswordForm()

    if form.validate_on_submit():
        User.query.get(user).set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль был изменен')
        return redirect(url_for('signin'))

    return render_template('reset_password_confirmed.html',
                           title='Новый пароль',
                           form=form)


@app.route('/business/<business>', methods=['GET', 'POST'])
def business_page(business):
    business = Business.query.filter(func.lower(Business.link) == business.lower()).first()
    if business is not None:
        return render_template('business.html',
                               business=business)
    else:
        abort(404)
