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

    id = db.Column(
        db.Integer,
        primary_key=True,
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

    @classmethod
    def register(cls,
                 username,
                 email,
                 first_name,
                 last_name,
                 zip_code,
                 password,
                 interests,
                 photo_url
                 #TODO: picture upload
                 ):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('utf8')

        print('in resgister block')
        user = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            zip_code = zip_code,
            hashed_password=hashed_pwd,
            interests=interests,
            photo_url=photo_url
            #TODO: picture upload
        )

        db.session.add(user)
        print('end of register block', user)
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


class Swipe(db.Model):
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


class Match(db.Model):
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




    """in our User model, we are going to add some static methods

1. get location from zip code
    function: getLocationFromZipCode()

    - geopy (pip install geopy)
    - from geopy.geocoders import Nominatim
    - geolocator = Nominatim(user_agent="geoapiExercises")
    - zipcode = "800011"
    - location = geolocator.geocode(zipcode)


    // or use google maps api

2. find users within that radius
    function: findUsersInRadius()




Postcodes don't map directly to a distance to each other.
You will have to acquire postcode & lat/long data,
look up the postcodes in there, and
compare the distance between the lat/long coordinates.


// getting lat / long from zip code
>>> from geopy.geocoders import Nominatim
>>> geolocator = Nominatim(user_agent="specify_your_app_name_here")
>>> geolocator.geocode({"postalcode": 10117})
Location(Mitte, Berlin, 10117, Deutschland, (52.5173269733757, 13.3881159334763, 0.0))
    """