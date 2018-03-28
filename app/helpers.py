from .models import Tag, Business
from flask_login import current_user
from flask import redirect, url_for, request, abort
from werkzeug.urls import url_parse
from functools import wraps
import math


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
        abort(404)
    if tag is None:
        items = Business.query.all()
    else:
        items = Tag.query.filter_by(name=tag).first().businesses

    if (page - 1) * 10 > len(items):
        abort(404)

    pages = math.ceil(len(items) / 10)
    if page * 10 <= len(items):
        items = items[(page - 1) * 10:page * 10]
    else:
        items = items[(page - 1) * 10:len(items)]

    return pages, items
