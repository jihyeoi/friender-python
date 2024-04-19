"""SQLAlchemy models for Warbler."""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from helpers import api_helpers
get_zips_in_radius = api_helpers.get_zips_in_radius

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_URL = (
    "https://icon-library.com/images/default-user-icon/" +
    "default-user-icon-28.jpg")


class User(db.Model):
    """user"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    username = db.Column(
        db.String(25),
        unique=True,
        nullable=False
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

    interests = db.Column(
        db.Text,
        nullable=False
    )

    photo_url = db.Column(
        db.Text,
        nullable=False,
        # TODO: default image
    )

    friend_radius = db.Column(
        db.Integer,
        nullable=False
    )


    @classmethod
    def register(cls,
                 username,
                 email,
                 first_name,
                 last_name,
                 zip_code,
                 password,
                 interests,
                 photo_url,
                 friend_radius
                 ):
        """
        Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('utf8')

        user = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            zip_code=zip_code,
            hashed_password=hashed_pwd,
            interests=interests,
            photo_url=photo_url,
            friend_radius=friend_radius
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """
        Find user with `username` and `password`.

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


class Swipe(db.Model):
    """a user has swipes"""

    __tablename__ = 'swipes'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    swiper_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )

    swipee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )

    # right is good, left is bad
    swipe_direction = db.Column(
        db.String(5),
        nullable=False
    )

    @classmethod
    def check_for_match(cls, swiper_id, swipee_id):
        '''
        Checks swipes of both users to determine if both swiped right, returns a boolean
        '''
        print(f'swiper {swiper_id} and swipee {swipee_id}')
        swipe = cls.query.filter_by(
            swiper_id=swiper_id, swipee_id=swipee_id).first()

        swipe_back = cls.query.filter_by(
            swiper_id=swipee_id, swipee_id=swiper_id).first()

        print('swipe is', swipe, swipe.swipe_direction)
        print('swipe_back is', swipe_back, swipe.swipe_direction)
        if swipe.swipe_direction == 'right' and swipe_back.swipe_direction == 'right':
            return True
        else:
            return False

    @classmethod
    def get_users_list(cls, user_id, num_miles):
        """
        list of users that logged in user can swipe on
        returns a list, list will be [] if swipavble users
        """

        swiped_user_ids = db.session.query(cls.swipee_id).filter(
            cls.swiper_id == user_id).subquery()

        all_users = db.session.query(User).filter(User.id != user_id)
        swipable_users = all_users.filter(
            User.id.notin_(swiped_user_ids)).all()
        user = User.query.get_or_404(user_id)
        zips_in_radius = get_zips_in_radius(user.zip_code, num_miles)
        print(zips_in_radius)

        swipable_users_ids = [user.id for user in swipable_users if user.zip_code in zips_in_radius]
        print(swipable_users_ids)

        return swipable_users_ids


class Match(db.Model):
    """a user can have matches"""

    __tablename__ = 'matches'

    match_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user1_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    user2_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    @classmethod
    def make_match(cls, swiper_id, swipee_id):
        ''' Checks if the two users are already matched, if not, creates new match '''
        print("from matches, swiper_id:", swiper_id)
        print("from matches, swipee_id:", swipee_id)

        match = cls(
            user1_id=swiper_id,
            user2_id=swipee_id,
        )
        print("match", match)

        db.session.add(match)


class Message(db.Model):
    """a user can send and receive messages"""

    __tablename__ = 'messages'

    message_id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
    )

    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="received_messages")
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)




