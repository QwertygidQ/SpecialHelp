from . import app, db
from .models import User
from .forms import SignInForm, SignUpForm
from flask import render_template, redirect, url_for


@app.route('/')
def index():
    return render_template('index.html',
                           title='Main Page')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))

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