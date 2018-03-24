from app import db, bcrypt, login_manager, app
from flask_login import UserMixin
from time import time
import jwt
import os
from PIL import Image

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

    image = db.relationship('Photo', backref='user', lazy='dynamic')

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


business_tag_table = db.Table('business-tag',
                              db.Column('business_id', db.Integer, db.ForeignKey('business.id')),
                              db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                              )


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), index=True, unique=True)

    def __repr__(self):
        return '<Tag {}>'.format(self.name)


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
    link = db.Column(db.String(50), index=True, unique=True)
    # image ??
    address = db.Column(db.String(300))  # is this enough for map APIs??
    time = db.Column(db.String(200))  # reserved for really big schedules; should change for searching???
    contacts = db.Column(db.String(200))
    tags = db.relationship('Tag', secondary=business_tag_table, backref='businesses', lazy='dynamic')
    rating = db.Column(db.SmallInteger, default=0)
    desc = db.Column(db.String(5000))
    comments = db.relationship('Comment', backref='business', lazy='dynamic')

    image = db.relationship('Photo', backref='to_business', lazy='dynamic')

    def recalculate_rating(self):
        if len(self.comments.all()) == 0:
            self.rating = 0
        else:
            self.rating = round(sum(comment.rating for comment in self.comments) / len(self.comments.all()), 1)
        db.session.commit()

    def __repr__(self):
        return '<Business {}>'.format(self.name)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(64), unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'))

    def clear_meta(self):
        ''' https://stackoverflow.com/a/23249933 '''
        image_file = open(os.path.join(app.config['UPLOAD_FOLDER'], self.filename))
        image = Image.open(image_file)

        # next 3 lines strip exif
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)

        image_without_exif.save(os.path.join(app.config['UPLOAD_FOLDER'], self.filename))

    def __repr__(self):
        return '<Photo #{0} at {1:.4}..{1:.4}>'.format(self.id, self.filename)
