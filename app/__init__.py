from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'signin'

from . import views, models, nl2br
from .admin_panel import AdminPanelIndexView, AdminPanelModelView

admin = Admin(app, index_view=AdminPanelIndexView())

admin.add_view(AdminPanelModelView(models.Business, db.session))
admin.add_view(AdminPanelModelView(models.User, db.session))
admin.add_view(AdminPanelModelView(models.Service, db.session))
admin.add_view(AdminPanelModelView(models.Comment, db.session))
