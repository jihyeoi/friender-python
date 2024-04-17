"""Forms for Friender."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, URL, Optional, InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed

class PhotoForm(FlaskForm):
    photo = FileField('Photo', validators=[
        FileRequired(),
        FileAllowed(["heic", "png", "jpg", "jpeg", "webp"], 'Images only!')
    ])

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

    zip_code = StringField(
        'Zipcode',
        validators=[DataRequired(), Length(min=5)]
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)],
    )

    interests = TextAreaField(
        'Interests',
        validators=[DataRequired()]
    )

    photo = FileField('Photo', validators=[
        FileRequired(),
        FileAllowed(["heic", "png", "jpg", "jpeg", "webp"], 'Images only!')
    ])
    #TODO: MAKE THIS AN UPLOAD FORM
    # TODO: need default image in static
    # TODO: ensure the picture is being uploaded to bucket correctly


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
        validators=[DataRequired(), Length(min=5)]
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


# class PictureUploadForm(FlaskForm):
#     """Picture Upload form."""

#     url = StringField(
#         'Picture URL',
#         validators=[DataRequired()],
#     )
