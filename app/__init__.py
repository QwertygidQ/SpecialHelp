from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_babelex import Babel, lazy_gettext

from flask.json import JSONEncoder

app = Flask(__name__)
app.config.from_object('config')

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            return str(obj)
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

from . import nl2br

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
babel = Babel(app)

login_manager = LoginManager(app)
login_manager.login_view = 'signin'
login_manager.login_message = lazy_gettext('Please log in to access this page.')

mail = Mail(app)

from . import views, models

from flask_admin import Admin
from .admin_panel import AdminPanelIndexView, AdminPanelModelView, BusinessCreationView, \
    UserCreationView, CommentCreationView, PhotoCreationView

admin = Admin(app, index_view=AdminPanelIndexView())

admin.add_view(BusinessCreationView(models.Business, db.session))
admin.add_view(AdminPanelModelView(models.Tag, db.session))
admin.add_view(PhotoCreationView(models.Photo, db.session))
admin.add_view(UserCreationView(models.User, db.session))
admin.add_view(CommentCreationView(models.Comment, db.session))
