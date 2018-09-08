from flask_mail import Message
from app import mail, app
from flask import render_template
from flask_babelex import gettext as _


def send_message(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients, body=text_body, html=html_body)
    mail.send(msg)


def send_reset_password_email(user):
    token = user.create_reset_password_token()
    send_message(_('[SpecialHelp] Password reset'), app.config['MAIL_USERNAME'], [user.email],
                 text_body=render_template('reset_password_email.txt',
                                           user=user,
                                           token=token),
                 html_body=render_template('reset_password_email.html',
                                           user=user,
                                           token=token))
