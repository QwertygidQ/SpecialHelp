#!/bin/sh

pip install -r requirements.txt
export FLASK_APP=main.py
flask db init
flask db migrate
flask db upgrade
python setup_helper.py
