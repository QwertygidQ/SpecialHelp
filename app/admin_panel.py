import logging

from flask import flash
from flask_admin import AdminIndexView, expose, form
from flask_admin.contrib.sqlamodel import ModelView
from flask_login import current_user
from flask import abort
from wtforms import TextAreaField, FileField
from . import image_upload
from .models import ROLE_ADMIN, ROLE_USER


def is_admin():
    return current_user.is_authenticated and current_user.role == ROLE_ADMIN


class AdminPanelIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if is_admin():
            return self.render('admin/index.html')
        else:
            abort(404)


class AdminPanelModelView(ModelView):
    def is_accessible(self):
        return is_admin()

    def inaccessible_callback(self, name, **kwargs):
        abort(404)


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
    can_create = False
    can_edit = False

    def delete_model(self, model):
        if model.__class__.__name__ != 'Comment':
            raise ValueError('Tried to delete ' + model.__class__.__name__ + ' in CommentCreationView, somehow')

        model_business = model.business
        super(CommentCreationView, self).delete_model(model)
        model_business.recalculate_rating()


class PhotoCreationView(AdminPanelModelView):
    form_excluded_columns = 'filename'
    form_extra_fields = dict(
        image=FileField()
    )

    def create_model(self, form):
        log = logging.getLogger("flask-admin.sqla")

        if form.user.data is not None and form.business.data is not None:
            flash('Failed to create record. Photo cannot be linked to both a user and a business.')
            log.error('Failed to create record. Photo cannot be linked to both a user and a business.')
            return False
        elif form.user.data is not None:
            owner_model = form.user.data
        elif form.business.data is not None:
            owner_model = form.business.data
        else:
            flash('Failed to create record. No user or business specified.')
            log.error('Failed to create record. No user or business specified.')
            return False

        if form.image.data is None:
            flash('Failed to create record. Image is not specified.')
            log.exception('Failed to create record. Image is not specified.')
            return False

        print(form.image, form.image.data)

        return_code = image_upload.save_photo(form.image.data, owner_model)
        if return_code != image_upload.SUCCESS:
            flash('Failed to create record. Error code: {}'.format(return_code), 'error')
            log.exception('Failed to create record. Error code: {}'.format(return_code))
            return False

        return owner_model.image
