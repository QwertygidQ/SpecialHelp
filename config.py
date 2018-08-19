import os
import sys
import random
import yaml

rand = random.SystemRandom()

host = '0.0.0.0'
port = 80
debug = True


def get_random_key(length=50):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(rand.choice(characters) for _ in range(length))


CSRF_ENABLED = True

SECRET_KEY = '-g0(m1l!@ew2pj8unyrf*s37pnkr&(+u0-^0_twic8v@5l6u3h'
if SECRET_KEY == '-g0(m1l!@ew2pj8unyrf*s37pnkr&(+u0-^0_twic8v@5l6u3h' and not debug:
    print('\x1b[31;1mIF YOU SEE THIS IN PRODUCTION - IMMEDIATELY CHANGE `SECRET_KEY`!!!\x1b[0m')
# SECRET_KEY = get_random_key()


if not os.path.isfile('db_config.yml'):
    print('You definitely need \'db_config.yml\'')
    sys.exit(-1)

uri = '{backend}://{username}:{passwd}@{server}:{port}/{dbname}'
with open('db_config.yml') as db_config:
    SQLALCHEMY_DATABASE_URI = uri.format(**yaml.load(db_config.read()))

SQLALCHEMY_TRACK_MODIFICATIONS = False


basedir = os.path.abspath(os.path.dirname(__name__))
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
IMG_FOLDER = os.path.join(basedir, 'static', 'images')
ALLOWED_IMG_FORMATS = ['jpg', 'jpeg', 'png']
ALLOWED_IMG_SIZE = 500 * 1024

LANGUAGES = ['en', 'ru']

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True

if not os.path.isfile('mail_config.yml'):
    print('You definitely need \'mail_config.yml\'')
    sys.exit(-1)

with open('mail_config.yml') as mail_config:
    yml = yaml.load(mail_config.read())
    MAIL_USERNAME = yml['username']
    MAIL_PASSWORD = yml['password']
