from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqlamodel import ModelView
from flask_login import current_user
from flask import abort
from wtforms import TextAreaField
from .models import ROLE_ADMIN, ROLE_USER


def is_admin():
    return current_user.is_authenticated and current_user.role == ROLE_ADMIN


class AdminPanelIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if is_admin():
            return self.render('admin/index.html')
        else:
            abort(403)


class AdminPanelModelView(ModelView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        abort(403)


class BusinessCreationView(AdminPanelModelView):
    form_excluded_columns = 'rating'

    form_overrides = dict(
        address=TextAreaField,
        time=TextAreaField,
        contacts=TextAreaField,
        desc=TextAreaField
    )


class UserCreationView(AdminPanelModelView):
    form_excluded_columns = 'password_hash'

    form_overrides = dict(
        contacts=TextAreaField,
        about=TextAreaField
    )

    form_choices = dict(
        role=[(str(ROLE_USER), 'User'), (str(ROLE_ADMIN), 'Admin')]
    )


class CommentCreationView(AdminPanelModelView):
    form_overrides = dict(
        text=TextAreaField
    )

    form_choices = dict(
        rating=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    )
