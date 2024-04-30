"""Tests for Flask Cafe."""


import os

os.environ["DATABASE_URL"] = "postgresql:///friender"
os.environ["FLASK_DEBUG"] = "0"

import re
from unittest import TestCase

from flask import session
from app import app, CURR_USER_KEY
from models import db, User, Match, Swipe, Message, connect_db

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()


#######################################
# helper functions for tests


def debug_html(response, label="DEBUGGING"):  # pragma: no cover
    """Prints HTML response; useful for debugging tests."""

    print("\n\n\n", "*********", label, "\n")
    print(response.data.decode('utf8'))
    print("\n\n")


def login_for_test(client, user_id):
    """Log in this user."""

    with client.session_transaction() as sess:
        sess[CURR_USER_KEY] = user_id


#######################################
# data to use for test objects / testing forms


TEST_USER_DATA = dict(
    username='b1',
    email='b1@gmail.com',
    zip_code='11565',
    first_name='b',
    last_name='b',
    interests='nature walks, doing nothing, watching tv',
    password="secret",
    photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/73eca85c-4c88-438c-aed8-9dd02e3288c4.JPG",
    friend_radius=25
)

TEST_USER_DATA_NEW = dict(
    username='c1',
    email='c1@gmail.com',
    zip_code='11565',
    first_name='c',
    last_name='c',
    interests='nature walks, doing nothing, watching tv',
    password="secret",
    photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/73eca85c-4c88-438c-aed8-9dd02e3288c4.JPG",
    friend_radius=25
)

# USER2 = User(
#     id=2,
#     username='b1',
#     email='b1@gmail.com',
#     zip_code='11565',
#     first_name='b',
#     last_name='b',
#     interests='nature walks, doing nothing, watching tv',
#     hashed_password="secret",
#     photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/73eca85c-4c88-438c-aed8-9dd02e3288c4.JPG",
#     friend_radius=25
# )

# USER1_EDIT = User(
#     id=1,
#     username='annie',
#     email='a1@gmail.com',
#     zip_code='92501',
#     first_name='a',
#     last_name='a',
#     interests='eating, running, fetching',
#     hashed_password="secret",
#     photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/dog.jpeg",
#     friend_radius=25
# )

# USER2_EDIT = User(
#     id=2,
#     username='b1',
#     email='b1@gmail.com',
#     zip_code='11565',
#     first_name='b',
#     last_name='b',
#     interests='nature walks, doing nothing, watching tv',
#     hashed_password="secret",
#     photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/dog.jpeg",
#     friend_radius=25
# )

# SWIPE1 = Swipe(
#     id=1,
#     swiper_id=1,
#     swipee_id=2,
#     swipe_direction='right'
# )

# SWIPE2 = Swipe(
#     id=2,
#     swiper_id=2,
#     swipee_id=1,
#     swipe_direction='right'
# )

# MATCH1 = Match(
#     match_id = 1,
#     user1_id = 1,
#     user2_id = 2
# )

# MESSAGE1 = Message(
#     message_id = 1,
#     sender_id = 1,
#     receiver_id=2,
#     content="hi"
# )

# MESSAGE2 = Message(
#     message_id = 2,
#     sender_id = 2,
#     receiver_id=1,
#     content="hii"
# )


#######################################
# homepage


class HomepageViewsTestCase(TestCase):
    """Tests about homepage."""

    def test_homepage(self):
        with app.test_client() as client:
            resp = client.get("/")
            self.assertIn(b'Do you miss making friends', resp.data)


# ######################################
# users


class UserModelTestCase(TestCase):
    """Tests for User Model."""

    def setUp(self):
        """Before all tests, add sample users"""

        User.query.delete()

        USER1 = User(
            id=1,
            username='a1',
            email='a1@gmail.com',
            zip_code='92501',
            first_name='a',
            last_name='a',
            interests='eating, running, fetching',
            hashed_password="$2b$12$oB1GmibCDWzbMfEWzNsjperI2NRbybHAnodeKbNRFdVa6IDUVstnu",
            photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/dog.jpeg",
            friend_radius=25
        )

        # USER2 = User(
        #     id=2,
        #     username='b1',
        #     email='b1@gmail.com',
        #     zip_code='11565',
        #     first_name='b',
        #     last_name='b',
        #     interests='nature walks, doing nothing, watching tv',
        #     hashed_password="secret",
        #     photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/73eca85c-4c88-438c-aed8-9dd02e3288c4.JPG",
        #     friend_radius=25
        # )

        db.session.add(USER1)

        db.session.commit()

        self.user1 = USER1

    def tearDown(self):
        """After each test, remove all cafes."""

        User.query.delete()
        db.session.commit()


    def test_authenticate(self):
        rez = User.authenticate("a1", "password")
        self.assertEqual(rez, self.user1)


    def test_authenticate_fail(self):
        rez = User.authenticate("no-such-user", "secret")
        self.assertFalse(rez)

        rez = User.authenticate("a1", "bad-password")
        self.assertFalse(rez)


    def test_register(self):
        u = User.register(**TEST_USER_DATA)
        self.assertEqual(u.hashed_password[:4], "$2b$")
        db.session.rollback()


class AuthViewsTestCase(TestCase):
    """Tests for views on logging in/logging out/registration."""

    def setUp(self):
        """Before each test, add sample users."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)
        db.session.add(user)

        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After each test, remove all users."""

        User.query.delete()
        db.session.commit()

    def test_signup(self):
        with app.test_client() as client:
            resp = client.get("/signup")
            self.assertIn(b'Join Friender today.', resp.data)

            resp = client.post(
                "/signup",
                data=TEST_USER_DATA_NEW,
                follow_redirects=True,
            )

            self.assertIn(b"Sign me up!", resp.data)
            # self.assertTrue(session.get(CURR_USER_KEY))

    # def test_signup_username_taken(self):
    #     with app.test_client() as client:
    #         resp = client.get("/signup")
    #         self.assertIn(b'Sign Up', resp.data)

    #         # signup with same data as the already-added user
    #         resp = client.post(
    #             "/signup",
    #             data=TEST_USER_DATA,
    #             follow_redirects=True,
    #         )

    #         self.assertIn(b"Username already taken", resp.data)

    def test_login(self):
        with app.test_client() as client:
            resp = client.get("/login")
            self.assertIn(b'Welcome back.', resp.data)

            resp = client.post(
                "/login",
                data={"username": "test", "password": "WRONG"},
                follow_redirects=True,
            )

            self.assertIn(b"Invalid credentials", resp.data)

            resp = client.post(
                "/login",
                data={"username": "test", "password": "secret"},
                follow_redirects=True,
            )

            self.assertIn(b"Invalid credentials.", resp.data)
            # self.assertEqual(session.get(CURR_USER_KEY), self.user_id)

    def test_logout(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.post("/logout", follow_redirects=True)

            self.assertIn(b"successfully logged out", resp.data)
            self.assertEqual(session.get(CURR_USER_KEY), None)


