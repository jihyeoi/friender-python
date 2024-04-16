"""Forms for Friender."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms import SelectField
from wtforms.validators import DataRequired, Email, Length, URL, Optional, InputRequired


class CSRFProtection(FlaskForm):
    """CSRFProtection form, intentionally has no fields."""


class SignupForm(FlaskForm):
    """Form for adding users on signup."""

    username = StringField(
        'Username',
        validators=[DataRequired()],
    )

    first_name = StringField(
        'First Name',
        validators=[DataRequired()],
    )

    last_name = StringField(
        'First Name',
        validators=[DataRequired()],
    )

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
    )

    zipcode = StringField(
        'Zipcode',
        validators=[DataRequired(min=6)]
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)],
    )

    profile_picture_url = StringField(
        'Image URL',
        validators=[URL(), Optional()],
    )


class ProfileEditForm(FlaskForm):
    """Form for editing a user profile."""

    first_name = StringField(
        'First Name',
        validators=[DataRequired()],
    )

    last_name = StringField(
        'First Name',
        validators=[DataRequired()],
    )

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
    )

    image_url = StringField(
        '(Optional) Image URL',
    )

    zipcode = StringField(
        'Zipcode',
        validators=[DataRequired(min=6)]
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[DataRequired()],
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()],
    )
