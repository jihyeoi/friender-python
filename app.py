import os
from dotenv import load_dotenv, dotenv_values
'''
accessing and printing value
os.getenv("MY_KEY")
'''
from flask import (
    Flask, render_template, request, flash, redirect, session, g, abort, url_for
)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import boto3
import random
from werkzeug.utils import secure_filename
from forms import (CSRFProtection, SignupForm, LoginForm, PhotoForm, SwipeForm)
from models import (
    db, connect_db, User, Match, Swipe, DEFAULT_IMAGE_URL)
from helpers import amazon_bucket_helpers, database_helpers
upload_photo = amazon_bucket_helpers.upload_photo
get_random_user = database_helpers.random_user_id


load_dotenv()
S3_KEY = os.getenv("S3_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_LOCATION = os.getenv("S3_LOCATION")
DATABASE_URL = os.getenv("DATABASE_URL")


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=SECRET_KEY
)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_only_form():
    """Add a CSRF-only form so that every route can use it."""

    g.csrf_form = CSRFProtection()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    do_logout()

    form = SignupForm()

    if form.validate_on_submit():
        try:
            photo_url = upload_photo(form.photo.data, form.username.data)
            print('inside try block of app', photo_url)
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                zip_code=form.zip_code.data,
                photo_url=photo_url,
                email=form.email.data,
                interests=form.interests.data
            )
            print("username in signup is", user.username)
            db.session.commit()
            print("it hit the commit")

        except IntegrityError as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login and redirect to homepage on success."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data,
        )

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.post('/logout')
def logout():
    """Handle logout of user and redirect to homepage."""

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


#######################################
# homepage

@app.get("/")
def homepage():
    """Show homepage."""

    if not g.user:
        return render_template('home_anon.html')

    return render_template("home.html")


##############################################################################
# Swipe routes:

@app.route("/swipes/<int:id>", methods=["GET", "POST"])
def swipe_results(id):
    """show swipe pages with buttons and handle results"""

    form = SwipeForm()

    if not g.user:
        flash("Please log in to make friends!")
        return redirect("/")

    swiper = g.user
    swipee = User.query.get_or_404(id)
    print("swipee from swipe route", swipee.first_name)

    print("G.USER", g.user.id)
    Swipe.get_users_list(swiper.id)


    if form.validate_on_submit():
        print('entered conditional in swipe')
        if form.left.data:
            swipe_result = Swipe(
                swiper_id=swiper.id,
                swipee_id=swipee.id,
                swipe_direction='left'
            )
            db.session.add(swipe_result)
            print("Swiped left", form.left.data)

        elif form.right.data:
            swipe_result = Swipe(
                swiper_id=swiper.id,
                swipee_id=swipee.id,
                swipe_direction='right'
            )
            db.session.add(swipe_result)
            if (Swipe.check_for_match(swiper_id=swiper.id, swipee_id=swipee.id)):
                Match.make_match(swiper_id=swiper.id, swipee_id=swipee.id)
                flash("you have a match!!! check your friends tab for more details", "success")
            print("Swiped right", form.right.data)

        print('after conditionals, before commit')
        db.session.commit()

        next_user_id= get_random_user()
        return redirect(f'/swipes/{next_user_id}')
        # Redirect or do something after handling the action

    return render_template("swipes.html",
                           swipee=swipee,
                           form=form)


# function to query a random user


