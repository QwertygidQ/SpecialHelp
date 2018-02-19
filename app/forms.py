from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional

from .models import User


class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=254)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=254)])
    username = StringField('Псевдоним', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Пароль', validators=[DataRequired(), EqualTo('repeat_password')])
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    # captcha TODO
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Этот Email уже занят, пожалуйста, выберите другой')


class UserUpdateForm(FlaskForm):
    email = StringField('Новый Email', validators=[Optional(), Email(), Length(max=254)])
    username = StringField('Новый псевдоним', validators=[Optional(), Length(max=50)])
    password = PasswordField('Новый пароль', validators=[Optional(), EqualTo('repeat_password')])
    repeat_password = PasswordField('Повторите новый пароль', validators=[Optional(), EqualTo('password')])

    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])

    user_update_submit = SubmitField('Обновить информацию')


class ProfileUpdateForm(FlaskForm):
    about = TextAreaField('О себе', validators=[Optional(), Length(max=500)])
    contacts = TextAreaField('Контакты', validators=[Optional(), Length(max=200)])

    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])

    profile_update_submit = SubmitField('Обновить информацию')
