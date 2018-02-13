from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqlamodel import ModelView

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

from . import views, models

admin = Admin(app)
admin.add_view(ModelView(models.Business, db.session))
admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Service, db.session))
admin.add_view(ModelView(models.Comment, db.session))
