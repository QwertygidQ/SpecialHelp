import os
import random

rand = random.SystemRandom()


def get_random_key(length=50):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(rand.choice(characters) for _ in range(length))


CSRF_ENABLED = True
SECRET_KEY = get_random_key()

basedir = os.path.abspath(os.path.dirname(__name__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')  # CHANGE TO A DIFFERENT DB!

SQLALCHEMY_TRACK_MODIFICATIONS = False
