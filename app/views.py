from . import app, db, email
from .models import User, Business, Comment, Tag
from .forms import SignInForm, SignUpForm, UserUpdateForm, ProfileUpdateForm,\
    PasswordResetForm, NewPasswordForm, CommentForm
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


def get_info_for_tag_and_validate(tag=None, page='1'):
    page = int(page)
    if page < 1:
        raise ValueError('non positive page')
    if tag is None:
        items = Business.query.all()
    else:
        items = Tag.query.filter_by(name=tag).first().businesses

    if ((page - 1) * 10 > len(items)):
        raise ValueError('invalid page')

    pages = len(items) // 10 + 1
    if page * 10 <= len(items):
        items = items[(page - 1) * 10:page * 10]
    else:
        items = items[(page - 1) * 10:len(items)]

    return pages, items


# ======================= View functions =======================

@app.route('/')
@app.route('/<pagination_page>')
def index(pagination_page=None):
    if pagination_page is None:
        return redirect(url_for('index', pagination_page='1'))

    try:
        pages, items = get_info_for_tag_and_validate(page=pagination_page)
    except ValueError:
        abort(400)

    return render_template('index.html',
                           title='Главная Страница',
                           pages_count=pages,
                           businesses=items)


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

        return redirect(url_for('signin'))

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


@app.route('/u/<username>')
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


@app.route('/b/<business_link>', methods=['GET', 'POST'])
def business_page(business_link):
    business = Business.query.filter(func.lower(Business.link) == business_link.lower()).first()
    if business is not None:
        form = None
        has_not_commented = current_user.is_authenticated and\
            current_user not in [comment.author for comment in business.comments]

        if has_not_commented:
            form = CommentForm()
            if form.validate_on_submit():
                rating = form.rating.data
                text = form.comment.data
                comment = Comment(rating=rating, text=text, business=business, author=current_user)
                db.session.add(comment)
                db.session.commit()

                business.recalculate_rating()

                flash('Ваш комментарий был отправлен')

                return redirect(url_for('business_page', business_link=business_link))

        return render_template('business.html',
                               title=business.name,
                               business=business,
                               has_not_commented=has_not_commented,
                               form=form)
    else:
        abort(404)


@app.route('/t/<tag_name>')
@app.route('/t/<tag_name>/<page>')
def tag_list_page(tag_name, page=1):
    if tag_name is None:
        abort(404)

    try:
        pages, items = get_info_for_tag_and_validate(tag_name, page)
    except ValueError:
        abort(400)

    return render_template('tag_list.html',
                            title='Организации по тегу ' + tag_name,
                            businesses=items,
                            pages_count = pages,
                            tag_name=tag_name)
