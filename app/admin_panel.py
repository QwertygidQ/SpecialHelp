from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqlamodel import ModelView
from flask_login import current_user
from flask import abort
from .models import ROLE_ADMIN

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
