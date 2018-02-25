from app import db, bcrypt, login_manager
from flask_login import UserMixin
from time import time
import jwt
from app import app

ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), index=True, unique=True)
    # avatar ??
    email = db.Column(db.String(254), index=True, unique=True)
    password_hash = db.Column(db.String(60))

    contacts = db.Column(db.String(200))
    about = db.Column(db.String(500))

    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    role = db.Column(db.SmallInteger, default=ROLE_USER)

    def __repr__(self):
        return '<User {}; {}>'.format(self.username, self.email)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def create_reset_password_token(self, expires_in=600):
        return jwt.encode({
            'reset-password': self.id,
            'exp': time() + expires_in
        }, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset-password']
        except:
            return None

        return id


@login_manager.user_loader
def loader(user_id):
    return User.query.get(int(user_id))


business_service_table = db.Table('business-service',
                                  db.Column('business_id', db.Integer, db.ForeignKey('business.id')),
                                  db.Column('service_id', db.Integer, db.ForeignKey('service.id'))
                                  )


class Service(db.Model):  # essentially, tags
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return '<Service {}>'.format(self.name)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.SmallInteger)
    text = db.Column(db.String(1000))

    business_id = db.Column(db.Integer, db.ForeignKey('business.id'))

    def __repr__(self):
        return '<Comment by {} on {}: {}>'.format(self.author.username, self.business.name, self.text)


class Business(db.Model):  # company/event
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), index=True, unique=True)
    # image ??
    address = db.Column(db.String(300))  # is this enough for map APIs??
    time = db.Column(db.String(200))  # reserved for really big schedules; should change for searching???
    contacts = db.Column(db.String(200))
    services = db.relationship('Service', secondary=business_service_table, backref='businesses', lazy='dynamic')
    rating = db.Column(db.SmallInteger, default=0)
    desc = db.Column(db.String(5000))
    comments = db.relationship('Comment', backref='business', lazy='dynamic')

    def __repr__(self):
        return '<Business {}>'.format(self.name)
