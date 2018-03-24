import os
import random

rand = random.SystemRandom()

host = 'localhost'
port = 8080
debug = True


def get_random_key(length=50):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(rand.choice(characters) for _ in range(length))


CSRF_ENABLED = True

SECRET_KEY = '-g0(m1l!@ew2pj8unyrf*s37pnkr&(+u0-^0_twic8v@5l6u3h'
if SECRET_KEY == '-g0(m1l!@ew2pj8unyrf*s37pnkr&(+u0-^0_twic8v@5l6u3h' and not debug:
    print('\x1b[31;1mIF YOU SEE THIS IN PRODUCTION - IMMEDIATELY CHANGE `SECRET_KEY`!!!\x1b[0m')
# SECRET_KEY = get_random_key()

basedir = os.path.abspath(os.path.dirname(__name__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')  # CHANGE TO A DIFFERENT DB!

SQLALCHEMY_TRACK_MODIFICATIONS = False

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
# MAIL_USERNAME = < username >
# MAIL_PASSWORD = < password >
