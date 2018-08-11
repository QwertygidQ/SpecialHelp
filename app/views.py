from . import app, db, email, babel
from .models import User, Business, Comment
from .forms import SignInForm, SignUpForm, UserUpdateForm, ProfileUpdateForm, \
    PasswordResetForm, NewPasswordForm, CommentForm, UserPictureUpdateForm
from .helpers import unauthenticated_required, get_next_page, get_info_for_tag_and_validate
from . import image_upload

from flask import render_template, redirect, url_for, flash, request, abort, session
from flask import send_from_directory, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_babelex import gettext
from sqlalchemy import func
import datetime


@babel.localeselector
def get_locale():
    if hasattr(current_user, 'locale') and current_user.locale != 'NONE':
        return current_user.locale
    elif 'locale' in session and session['locale'] in app.config['LANGUAGES']:
        return session['locale']

    return request.accept_languages.best_match(app.config['LANGUAGES'])


@app.route('/')
def index():
    pagination_page = request.args.get('page')
    if pagination_page is None:
        return redirect(url_for('index', page='1'))

    try:
        pages, items = get_info_for_tag_and_validate(page=pagination_page)

        return render_template('index.html',
                               title=gettext('Main page'),
                               pages_count=pages,
                               businesses=items)
    except ValueError:
        abort(400)


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
            flash(gettext('Invalid email or password'), 'error')

    return render_template('signin.html',
                           title=gettext('Sign in'),
                           form=form)

@app.route('/signup', methods=['GET', 'POST'])
@unauthenticated_required
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('signin', next=get_next_page()))

    return render_template('signup.html',
                           title=gettext('Registration'),
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
                           title=gettext("%(username)s's profile", username=username),
                           user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    userform = UserUpdateForm()
    profileform = ProfileUpdateForm()
    pictureform = UserPictureUpdateForm()

    if pictureform.picture_update_submit.data and pictureform.validate_on_submit():
        return_code = image_upload.save_photo(pictureform.picture.data,
                                              current_user)  # do we need a password check here??
        if return_code == image_upload.SUCCESS:
            flash(gettext('Profile saved'), 'message')
            return redirect(url_for('profile', username=current_user.username))
        elif return_code == image_upload.INVALID_FORMAT:
            flash(gettext('Invalid file format'), 'error')
        elif return_code == image_upload.INVALID_FILENAME:
            flash(gettext('Invalid filename'), 'error')
        elif return_code == image_upload.INVALID_SIZE:
            flash(gettext('File is too large'), 'error')

    elif userform.user_update_submit.data and userform.validate_on_submit():
        if current_user.check_password(userform.current_password.data):
            if userform.email.data != '':
                current_user.email = userform.email.data

            if userform.username.data != '':
                current_user.username = userform.username.data

            if userform.password.data != '':
                current_user.set_password(userform.password.data)

            db.session.commit()

            flash(gettext('Profile saved'), 'message')
            return redirect(url_for('profile', username=current_user.username))
        else:
            flash(gettext('Invalid current password'), 'error')
    elif profileform.profile_update_submit.data and profileform.validate_on_submit():
        if current_user.check_password(userform.current_password.data):
            if profileform.about.data != '':
                current_user.about = profileform.about.data

            if profileform.contacts.data != '':
                current_user.contacts = profileform.contacts.data

            db.session.commit()

            flash(gettext('Profile saved'), 'message')
            return redirect(url_for('profile', username=current_user.username))
        else:
            flash(gettext('Invalid current password'), 'error')

    return render_template('edit_profile.html',
                           title=gettext('Change profile settings'),
                           userform=userform,
                           profileform=profileform,
                           pictureform=pictureform,
                           user=current_user)


@app.route('/reset_password', methods=['GET', 'POST'])
@unauthenticated_required
def reset_password():
    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == form.email.data.lower()).first()
        if user is not None:
            email.send_reset_password_email(user)
            flash(gettext('Message with a password reset link has been sent to your email'), 'message')

            return redirect(url_for('signin'))
        else:
            flash(gettext('User with this email does not exist'), 'error')

    return render_template('reset_password.html',
                           title=gettext('Reset password'),
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
        flash(gettext('Your password has been changed'), 'message')
        return redirect(url_for('signin'))

    return render_template('reset_password_confirmed.html',
                           title=gettext('New password'),
                           form=form)


@app.route('/b/<business_link>', methods=['GET', 'POST'])
def business_page(business_link):
    business = Business.query.filter(func.lower(Business.link) == business_link.lower()).first()
    if business is not None:
        form = None
        has_not_commented = current_user.is_authenticated and \
                            current_user not in [comment.author for comment in business.comments]

        if has_not_commented:
            form = CommentForm()
            if form.validate_on_submit():
                try:
                    rating = int(form.rating.data)
                except ValueError:
                    abort(400)

                if rating < 1 or rating > 5:
                    abort(400)

                text = form.comment.data
                comment = Comment(rating=rating, text=text, business=business, author=current_user)
                db.session.add(comment)
                db.session.commit()

                business.recalculate_rating()

                flash(gettext('Your comment has been posted'), 'message')

                return redirect(url_for('business_page', business_link=business_link))

        return render_template('business.html',
                               title=business.name,
                               business=business,
                               has_not_commented=has_not_commented,
                               form=form)
    else:
        abort(404)


@app.route('/t/<tag_name>')
def tag_list_page(tag_name):
    if tag_name is None:
        abort(404)

    page = request.args.get('page')
    if page is None:
        return redirect(url_for('tag_list_page', tag_name=tag_name, page='1'))

    try:
        pages, items = get_info_for_tag_and_validate(tag_name, page)

        return render_template('tag_list.html',
                               title=gettext('Businesses for tag %(tag)s', tag=tag_name),
                               businesses=items,
                               pages_count=pages,
                               tag_name=tag_name)
    except ValueError:
        abort(400)


@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/locale')
def change_locale():
    new_locale = request.args.get('lang')
    if new_locale is None or new_locale not in app.config['LANGUAGES']:
        return redirect(get_next_page())

    if current_user.is_authenticated:
        current_user.locale = new_locale
        db.session.commit()

    session['locale'] = new_locale

    return redirect(get_next_page())

@app.route('/get_businesses', methods=['POST'])
def get_businesses():
    err_json = jsonify({'status': 'error', 'desc': 'Got invalid data from the client.'})

    if not request.json or not all(param in request.json for param in ['type', 'page', 'reverse']):
        return err_json

    sort_type = request.json['type']
    if sort_type not in ['location', 'alphabet', 'date', 'rating']:
        return err_json

    page = request.json['page']
    reverse = request.json['reverse']
    if type(page) != int or type(reverse) != bool:
        return err_json

    if sort_type == 'location':
        if not all(param in request.json for param in ['lat', 'lon', 'max_dist']):
            return err_json

        lat = request.json['lat']
        lon = request.json['lon']
        coords = (lat, lon)
        max_dist = request.json['max_dist']

        if type(lat) != float or type(lon) != float or type(max_dist) != int:
            return err_json

        if not -90.0 <= lat <= 90.0 or not -180.0 <= lon <= 180.0: # TODO: properly check float ranges?
            return err_json

        MAX_DIST_CAP = 50000 # meters
        if not 0 <= max_dist <= MAX_DIST_CAP:
            return err_json

        def location_query(user_coords, max_dist, reverse):
            dist = Business.calculate_dist_to_user(user_coords)
            query = Business.query.filter(dist <= max_dist)

            if reverse:
                return query.order_by(dist.desc())
            return query.order_by(dist)

        query = location_query(coords, max_dist, reverse)
    elif sort_type == 'alphabet':
        if reverse:
            query = Business.query.order_by(Business.name.desc())
        else:
            query = Business.query.order_by(Business.name)
    elif sort_type == 'rating':
        if 'min_rating' not in request.json:
            return err_json

        min_rating = request.json['min_rating']
        if type(min_rating) != int or not 0 <= min_rating <= 5:
            return err_json

        query = Business.query.filter(Business.rating >= min_rating)

        if reverse:
            query = query.order_by(Business.rating)
        else:
            query = query.order_by(Business.rating.desc()) # we want to normally show the highest rating first

    else: # TODO: add date sorting
        return err_json

    businesses = query.paginate(page, 10, False).items
    if not businesses:
        abort(404)
    print(businesses) # TODO: add functionality

    return jsonify({'status': 'ok'})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
