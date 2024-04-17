"""SQLAlchemy models for Warbler."""

# from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_URL = (
    "https://icon-library.com/images/default-user-icon/" +
    "default-user-icon-28.jpg")

class User(db.Model):
    """user"""

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

    hashed_password = db.Column(
        db.String(100),
        nullable=False
    )

    profile_picture_url = db.Column(
        db.String(100),
        nullable=False,
        default=DEFAULT_IMAGE_URL
    )

    @classmethod
    def register(cls,
                 username,
                 email,
                 first_name,
                 last_name,
                 zip_code,
                 password,
                 profile_picture_url=None):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('utf8')

        user = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            zip_code = zip_code,
            hashed_password=hashed_pwd,
            profile_picture_url=profile_picture_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.hashed_password, password):
            return user
        else:
            return False


class Interests(db.Model):
    """A user can have interests"""

    __tablename__ = 'interests'

    interest_id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(50),
        nullable=False
    )


class User_Interests(db.Model):
    """join table for users and interests """

    __tablename__ = 'user_interests'

    user_interest_id = db.Column(
        db.Integer,
        primary_key = True
    )

    username = db.Column(
        db.String(25),
        db.ForeignKey('users.username'),
        primary_key = True
    )

    interest_id = db.Column(
        db.Integer,
        db.ForeignKey('interests.interest_id'),
        primary_key = True
    )

    user = db.relationship('User', backref='user_interests')
    interests = db.relationship('Interests', backref='interests')


class Swipes(db.Model):
    """a user has swipes"""

    __tablename__ = 'swipes'

    swipe_id = db.Column(
        db.Integer,
        primary_key = True
    )

    swiper_username = db.Column(
        db.String(25),
        db.ForeignKey('users.username'),
        primary_key = True
    )

    swipee_username = db.Column(
        db.String(25),
        db.ForeignKey('users.username'),
        primary_key = True
    )


class Matches(db.Model):
    """a user can have matches"""

    __tablename__ = 'matches'

    match_id = db.Column(
        db.Integer,
        primary_key = True
    )

    first_username = db.Column(
        db.String(25),
        db.ForeignKey('users.username'),
        primary_key = True
    )

    second_username = db.Column(
        db.String(25),
        db.ForeignKey('users.username'),
        primary_key = True
    )

class Message(db.Model):
    """a user can send and receive messages"""

    __tablename__ = 'messages'

    message_id = db.Column(
        db.Integer,
        primary_key = True
    )

    sender_username = db.Column(
        db.String(25),
        db.ForeignKey('users.username'),
        primary_key = True
    )

    receiver_username = db.Column(
        db.String(25),
        db.ForeignKey('users.username'),
        primary_key = True
    )

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
