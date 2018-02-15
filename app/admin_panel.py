from flask_admin.contrib.sqlamodel import ModelView
from flask_login import current_user
from flask import abort
from . import admin, db
from .models import User, Business, Service, Comment, ROLE_ADMIN

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == ROLE_ADMIN

    def inaccessible_callback(self, name, **kwargs):
        abort(403)

admin.add_view(AdminModelView(Business, db.session))
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Service, db.session))
admin.add_view(AdminModelView(Comment, db.session))
