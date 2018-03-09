from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'signin'

mail = Mail(app)

from . import views, models, nl2br

from flask_admin import Admin
from .admin_panel import AdminPanelIndexView, AdminPanelModelView, BusinessCreationView,\
    UserCreationView, CommentCreationView

admin = Admin(app, index_view=AdminPanelIndexView())

admin.add_view(BusinessCreationView(models.Business, db.session))
admin.add_view(UserCreationView(models.User, db.session))
admin.add_view(AdminPanelModelView(models.Tag, db.session))
admin.add_view(CommentCreationView(models.Comment, db.session))
