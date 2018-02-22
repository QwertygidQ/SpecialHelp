from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional

from .models import User


# Customized validators

def msg_DataRequired():
    return DataRequired(message='Это обязательное поле')


def msg_Length(min=-1, max=-1):
    if min >= 1 and max >= 1:
        message = 'Длина поля должна быть между {} и {} символами'.format(min, max)
    elif min >= 1:
        message = 'Длина поля должна быть не меньше {} символов'.format(min)
    elif max >= 1:
        message = 'Длина поля должна быть не больше {} символов'.format(max)

    return Length(min=min, max=max, message=message)


def msg_Email():
    return Email(message='Указан невалидный Email адрес')


def msg_password_EqualTo(field):
    return EqualTo(field, message='Пароли должны совпадать')


class StrippedStringField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].strip()
        else:
            self.data = ''


class StrippedTextAreaField(TextAreaField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].strip()
        else:
            self.data = ''


class SignInForm(FlaskForm):
    email = StrippedStringField('Email', validators=[msg_DataRequired(), msg_Email(), msg_Length(max=254)])
    password = PasswordField('Пароль', validators=[msg_DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EmailUsernameForm(FlaskForm):
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Этот Email уже занят, пожалуйста, выберите другой')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Этот псевдоним уже занят, пожалуйста, выберите другой')


class SignUpForm(EmailUsernameForm):
    email = StrippedStringField('Email', validators=[msg_DataRequired(), msg_Email(), msg_Length(max=254)])
    username = StrippedStringField('Псевдоним', validators=[msg_DataRequired(), msg_Length(max=50)])
    password = PasswordField('Пароль', validators=[msg_DataRequired(), msg_password_EqualTo('repeat_password')])
    repeat_password = PasswordField('Повторите пароль', validators=[msg_DataRequired(),
                                                                    msg_password_EqualTo('password')])
    # captcha TODO
    submit = SubmitField('Зарегистрироваться')


class UserUpdateForm(EmailUsernameForm):
    email = StrippedStringField('Новый Email', validators=[Optional(), msg_Email(), msg_Length(max=254)])
    username = StrippedStringField('Новый псевдоним', validators=[Optional(), msg_Length(max=50)])
    password = PasswordField('Новый пароль', validators=[Optional(), msg_password_EqualTo('repeat_password')])
    repeat_password = PasswordField('Повторите новый пароль', validators=[Optional(), msg_password_EqualTo('password')])

    current_password = PasswordField('Текущий пароль', validators=[msg_DataRequired()])

    user_update_submit = SubmitField('Обновить информацию')


class ProfileUpdateForm(FlaskForm):
    about = StrippedTextAreaField('О себе', validators=[Optional(), msg_Length(max=500)])
    contacts = StrippedTextAreaField('Контакты', validators=[Optional(), msg_Length(max=200)])

    current_password = PasswordField('Текущий пароль', validators=[msg_DataRequired()])

    profile_update_submit = SubmitField('Обновить информацию')
