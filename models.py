"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_URL = (
    "https://icon-library.com/images/default-user-icon/" +
    "default-user-icon-28.jpg")

class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(
        db.String(25),
        primary_key=True
    )

    email = db.Column(
        db.String(50),
        nullable=False
    )

    zip_code = db.Column(
        db.String(5),
        nullable=False
    )

    first_name = db.Column(
        db.String(25),
        nullable=False
    )

    last_name = db.Column(
        db.String(25),
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    profile_picture_url = db.Column(
        db.String(100),
        nullable=False
    )


class Interests(db.Model):

    __tablename__ = 'interests'

    interest_id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(50),
        nullable=False
    )

class User_Interests(
    __tablename__ = 'user_interests'
)
