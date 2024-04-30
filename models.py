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

    def get_message(self):
        messages_sent = Message.query.filter_by(sender_id = self.id).all()
        messages_received = Message.query.filter_by(receiver_id = self.id).all()
        return messages_sent, messages_received

    def get_matches(self):
        matches = Match.query.filter(
            (Match.user1_id == self.id) | (Match.user2_id == self.id)
        ).all()

        user_matches = []

        for match in matches:
        # Get the details of the other user in each match
            other_user_id = match.user2_id if match.user1_id == self.id else match.user1_id
            other_user = User.query.get(other_user_id)  # Assuming you have a User model with username
            user_matches.append((match.match_id, other_user.username))

        return user_matches



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

        if swipe and swipe_back:
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

        user = User.query.get(user_id)
        if not user:
            return []

        zips_in_radius = get_zips_in_radius(user.zip_code, num_miles)
        test_zips = get_zips_in_radius(92501, 10)
        print(test_zips, "TEST!!!!!!!!!!!!")

        # users already swiped on
        swiped_user_ids = db.session.query(cls.swipee_id).filter(
            cls.swiper_id == user_id
        ).subquery()

        # get swipable users by filtering out swiped users and those not in desired zip code
        swipable_users = db.session.query(User.id).filter(
            User.id != user_id,
            User.zip_code.in_(zips_in_radius),
            User.id.notin_(swiped_user_ids)
        ).all()

        # extract user IDs from query result
        swipable_users_ids = [user.id for user in swipable_users]

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

        match = cls(
            user1_id=swiper_id,
            user2_id=swipee_id,
        )

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




