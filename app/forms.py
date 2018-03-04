from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, ValidationError, Length, Optional
from sqlalchemy import func
from .models import User


# ======================= Customized validators =======================


def msg_DataRequired():  # for use with stripped fields
    return DataRequired(message='Это обязательное поле')


def msg_InputRequired():  # for use with everything else (password fields, etc.)
    return InputRequired(message='Это обязательное поле')


def msg_Length(min=-1, max=-1):
    if min >= 1 and max >= 1:
        message = 'Длина поля должна быть между {} и {} символами'.format(min, max)
    elif min >= 1:
        message = 'Длина поля должна быть не меньше {} символов'.format(min)
    elif max >= 1:
        message = 'Длина поля должна быть не больше {} символов'.format(max)
    else:
        message = None  # an error condition anyway (assertion fails in __init__ of Length)

    return Length(min=min, max=max, message=message)


def msg_Email():
    return Email(message='Указан невалидный Email адрес')


def msg_password_Length():
    min = 6
    message = 'Длина пароля не может быть меньше {} символов'.format(min)
    return Length(min=min, message=message)


def msg_password_EqualTo(field):
    return EqualTo(field, message='Пароли должны совпадать')


def unique_email():
    message = 'Этот Email уже занят, пожалуйста, выберите другой'

    def _unique_email(_, field):
        user = User.query.filter(func.lower(User.email) == field.data.lower()).first()
        if user is not None:
            raise ValidationError(message)

    return _unique_email


def unique_username():
    message = 'Этот псевдоним уже занят, пожалуйста, выберите другой'

    def _unique_username(_, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError(message)

    return _unique_username


# ======================= Stripped fields =======================


class StrippedField:
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].strip()
        else:
            self.data = ''


class StrippedStringField(StrippedField, StringField):
    pass


class StrippedTextAreaField(StrippedField, TextAreaField):
    pass


# ======================= Forms =======================


class SignInForm(FlaskForm):
    email = StrippedStringField('Email', validators=[
        msg_DataRequired(),
        msg_Email(),
        msg_Length(max=254)
    ])
    password = PasswordField('Пароль', validators=[
        msg_InputRequired(),
        msg_password_Length()
    ])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignUpForm(FlaskForm):
    email = StrippedStringField('Email', validators=[
        msg_DataRequired(),
        msg_Email(),
        unique_email(),
        msg_Length(max=254)
    ])
    username = StrippedStringField('Псевдоним', validators=[
        msg_DataRequired(),
        msg_Length(max=50),
        unique_username()
    ])
    password = PasswordField('Пароль', validators=[
        msg_InputRequired(),
        msg_password_EqualTo('repeat_password'),
        msg_password_Length()
    ])
    repeat_password = PasswordField('Повторите пароль', validators=[
        msg_InputRequired(),
        msg_password_EqualTo('password'),
        msg_password_Length()
    ])
    # captcha TODO
    submit = SubmitField('Зарегистрироваться')


class UserUpdateForm(FlaskForm):
    email = StrippedStringField('Новый Email', validators=[
        Optional(),
        msg_Email(),
        unique_email(),
        msg_Length(max=254)
    ])
    username = StrippedStringField('Новый псевдоним', validators=[
        Optional(),
        msg_Length(max=50),
        unique_username()
    ])
    password = PasswordField('Новый пароль', validators=[
        Optional(strip_whitespace=False),
        msg_password_EqualTo('repeat_password'),
        msg_password_Length()
    ])
    repeat_password = PasswordField('Повторите новый пароль', validators=[
        Optional(strip_whitespace=False),
        msg_password_EqualTo('password'),
        msg_password_Length()
    ])

    current_password = PasswordField('Текущий пароль', validators=[
        msg_InputRequired(),
        msg_password_Length()
    ])

    user_update_submit = SubmitField('Обновить информацию')


class ProfileUpdateForm(FlaskForm):
    about = StrippedTextAreaField('О себе', validators=[
        Optional(),
        msg_Length(max=500)
    ])
    contacts = StrippedTextAreaField('Контакты', validators=[
        Optional(),
        msg_Length(max=200)
    ])

    current_password = PasswordField('Текущий пароль', validators=[
        msg_InputRequired(),
        msg_password_Length()
    ])

    profile_update_submit = SubmitField('Обновить информацию')


class PasswordResetForm(FlaskForm):
    email = StrippedStringField('Email', validators=[
        msg_DataRequired(),
        msg_Email(),
        msg_Length(max=254)
    ])

    submit = SubmitField('Сбросить пароль')


class NewPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[
        Optional(strip_whitespace=False),
        msg_password_EqualTo('repeat_password'),
        msg_password_Length()
    ])

    repeat_password = PasswordField('Повторите новый пароль', validators=[
        Optional(strip_whitespace=False),
        msg_password_EqualTo('password'),
        msg_password_Length()
    ])

    submit = SubmitField('Сбросить пароль')


class CommentForm(FlaskForm):
    rating = SelectField('Оценка', choices=[(str(x), str(x)) for x in range(1, 6)])

    comment = StrippedTextAreaField('Комментарий', validators=[
        msg_DataRequired(),
        msg_Length(max=1000)
    ])

    submit = SubmitField('Оставить комментарий')
