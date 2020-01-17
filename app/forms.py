from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Email,
    EqualTo,
    ValidationError,
    Length,
    Optional,
)
from sqlalchemy import func
from .models import User
from flask_babelex import lazy_gettext


# ======================= Customized validators =======================


def msg_DataRequired():  # for use with stripped fields
    return DataRequired(message=lazy_gettext("This field is required"))


def msg_FileRequired():  # for use with file upload fields
    return FileRequired(message=lazy_gettext("This field is required"))


def msg_InputRequired():  # for use with everything else (password fields, etc.)
    return InputRequired(message=lazy_gettext("This field is required"))


def msg_Length(min=-1, max=-1):
    if min >= 1 and max >= 1:
        message = lazy_gettext(
            "Field length must be between %(min)s and %(max)s characters",
            min=min,
            max=max,
        )
    elif min >= 1:
        message = lazy_gettext(
            "Field length must be at least %(min)s characters", min=min
        )
    elif max >= 1:
        message = lazy_gettext(
            "Field cannot be longer than %(max)s characters", max=max
        )
    else:
        message = (
            None  # an error condition anyway (assertion fails in __init__ of Length)
        )

    return Length(min=min, max=max, message=message)


def msg_Email():
    return Email(message=lazy_gettext("Invalid email address"))


def msg_password_Length():
    min = 6
    message = lazy_gettext(
        "Password length must be at least %(min)s characters", min=min
    )
    return Length(min=min, message=message)


def msg_password_EqualTo(field):
    return EqualTo(field, message=lazy_gettext("Passwords must match"))


def unique_email():
    message = lazy_gettext("This email is already taken")

    def _unique_email(_, field):
        user = User.query.filter(func.lower(User.email) == field.data.lower()).first()
        if user is not None:
            raise ValidationError(message)

    return _unique_email


def unique_username():
    message = lazy_gettext("This username is already taken")

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
            self.data = ""


class StrippedStringField(StrippedField, StringField):
    pass


class StrippedTextAreaField(StrippedField, TextAreaField):
    pass


# ======================= Forms =======================


class SignInForm(FlaskForm):
    email = StrippedStringField(
        lazy_gettext("Email"),
        validators=[msg_DataRequired(), msg_Email(), msg_Length(max=254)],
    )
    password = PasswordField(
        lazy_gettext("Password"),
        validators=[msg_InputRequired(), msg_password_Length()],
    )
    remember = BooleanField(lazy_gettext("Remember me"))
    submit = SubmitField(lazy_gettext("Sign in"))


class SignUpForm(FlaskForm):
    email = StrippedStringField(
        lazy_gettext("Email"),
        validators=[
            msg_DataRequired(),
            msg_Email(),
            unique_email(),
            msg_Length(max=254),
        ],
    )
    username = StrippedStringField(
        lazy_gettext("Username"),
        validators=[msg_DataRequired(), msg_Length(max=50), unique_username()],
    )
    password = PasswordField(
        lazy_gettext("Password"),
        validators=[
            msg_InputRequired(),
            msg_password_EqualTo("repeat_password"),
            msg_password_Length(),
        ],
    )
    repeat_password = PasswordField(
        lazy_gettext("Repeat password"),
        validators=[
            msg_InputRequired(),
            msg_password_EqualTo("password"),
            msg_password_Length(),
        ],
    )
    # captcha TODO
    submit = SubmitField(lazy_gettext("Register"))


class UserPictureUpdateForm(FlaskForm):
    picture = FileField(lazy_gettext("Picture"), validators=[msg_FileRequired()])

    picture_update_submit = SubmitField(lazy_gettext("Upload new picture"))


class UserUpdateForm(FlaskForm):
    email = StrippedStringField(
        lazy_gettext("New email"),
        validators=[Optional(), msg_Email(), unique_email(), msg_Length(max=254)],
    )
    username = StrippedStringField(
        lazy_gettext("New username"),
        validators=[Optional(), msg_Length(max=50), unique_username()],
    )
    password = PasswordField(
        lazy_gettext("New password"),
        validators=[
            Optional(strip_whitespace=False),
            msg_password_EqualTo("repeat_password"),
            msg_password_Length(),
        ],
    )
    repeat_password = PasswordField(
        lazy_gettext("Repeat new password"),
        validators=[
            Optional(strip_whitespace=False),
            msg_password_EqualTo("password"),
            msg_password_Length(),
        ],
    )

    current_password = PasswordField(
        lazy_gettext("Current password"),
        validators=[msg_InputRequired(), msg_password_Length()],
    )

    user_update_submit = SubmitField(lazy_gettext("Update information"))


class ProfileUpdateForm(FlaskForm):
    about = StrippedTextAreaField(
        lazy_gettext("About me"), validators=[Optional(), msg_Length(max=500)]
    )
    contacts = StrippedTextAreaField(
        lazy_gettext("Contacts"), validators=[Optional(), msg_Length(max=200)]
    )

    current_password = PasswordField(
        lazy_gettext("Current password"),
        validators=[msg_InputRequired(), msg_password_Length()],
    )

    profile_update_submit = SubmitField(lazy_gettext("Update information"))


class PasswordResetForm(FlaskForm):
    email = StrippedStringField(
        lazy_gettext("Email"),
        validators=[msg_DataRequired(), msg_Email(), msg_Length(max=254)],
    )

    submit = SubmitField(lazy_gettext("Reset password"))


class NewPasswordForm(FlaskForm):
    password = PasswordField(
        lazy_gettext("New password"),
        validators=[
            msg_InputRequired(),
            msg_password_EqualTo("repeat_password"),
            msg_password_Length(),
        ],
    )

    repeat_password = PasswordField(
        lazy_gettext("Repeat new password"),
        validators=[
            msg_InputRequired(),
            msg_password_EqualTo("password"),
            msg_password_Length(),
        ],
    )

    submit = SubmitField(lazy_gettext("Update password"))


class CommentForm(FlaskForm):
    rating = HiddenField(lazy_gettext("Rating"), default="4")

    comment = StrippedTextAreaField(
        lazy_gettext("Comment"), validators=[msg_DataRequired(), msg_Length(max=1000)]
    )

    submit = SubmitField(lazy_gettext("Post comment"))
