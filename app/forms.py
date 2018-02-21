from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional

from .models import User


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
    email = StrippedStringField('Email', validators=[DataRequired(), Email(), Length(max=254)])
    password = PasswordField('Пароль', validators=[DataRequired()])
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
    email = StrippedStringField('Email', validators=[DataRequired(), Email(), Length(max=254)])
    username = StrippedStringField('Псевдоним', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Пароль', validators=[DataRequired(), EqualTo('repeat_password')])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    # captcha TODO
    submit = SubmitField('Зарегистрироваться')


class UserUpdateForm(EmailUsernameForm):
    email = StrippedStringField('Новый Email', validators=[Optional(), Email(), Length(max=254)])
    username = StrippedStringField('Новый псевдоним', validators=[Optional(), Length(max=50)])
    password = PasswordField('Новый пароль', validators=[Optional(), EqualTo('repeat_password')])
    repeat_password = PasswordField('Повторите новый пароль', validators=[Optional(), EqualTo('password')])

    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])

    user_update_submit = SubmitField('Обновить информацию')


class ProfileUpdateForm(FlaskForm):
    about = StrippedTextAreaField('О себе', validators=[Optional(), Length(max=500)])
    contacts = StrippedTextAreaField('Контакты', validators=[Optional(), Length(max=200)])

    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])

    profile_update_submit = SubmitField('Обновить информацию')
