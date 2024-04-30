import os
from dotenv import load_dotenv
from flask import ( Flask, request, render_template, flash, redirect, session, g )
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
import boto3

from forms import ( CSRFProtection, SignupForm, LoginForm, NewMessageForm,
                   SwipeForm, ProfileEditForm )
from models import (
    db, connect_db, User, Match, Swipe, Message, DEFAULT_IMAGE_URL)
from helpers import amazon_bucket_helpers, database_helpers, api_helpers
upload_photo = amazon_bucket_helpers.upload_photo
get_random_user = database_helpers.random_user_id
get_zips_in_radius = api_helpers.get_zips_in_radius


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
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
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
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                zip_code=form.zip_code.data,
                photo_url=photo_url,
                email=form.email.data,
                interests=form.interests.data,
                friend_radius=form.friend_radius.data
            )
            db.session.commit()

        except IntegrityError:
            flash(f"That username is already taken, please try again", 'danger')
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
    form = g.csrf_form

    if not g.user:
        return render_template('home_anon.html')

    return render_template("home.html", form=form)


#######################################
# user profile

@app.get("/profile")
def profile_page():
    """Show profile page."""
    if not g.user:
        return render_template('home_anon.html')
    return render_template("users/profile.html")


@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    """edit profile"""

    if not g.user:
        flash("Please log in to access this page!")
        return redirect("/login")

    user = g.user

    form = ProfileEditForm(obj=user)

    if form.validate_on_submit():
        try:
            if 'photo' in request.files and request.files['photo'].filename != '':
                photo = request.files['photo']
                photo_url = upload_photo(photo, user.username)
                user.photo_url = photo_url

            user.first_name =form.first_name.data
            user.last_name=form.last_name.data
            user.email = form.email.data
            user.friend_radius = form.friend_radius.data
            user.interests = form.interests.data
            user.zip_code = form.zip_code.data

            db.session.commit()

            flash("Profile edited!")
            return redirect("/profile")

        except IntegrityError as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')
            return render_template('users/profile_edit.html', form=form)

    return render_template('users/profile_edit.html', form=form)


##############################################################################
# Swipe routes:

@app.post("/swipes/new")
def redirect_to_swipes():
    """landing page for swiping"""

    next_user_id = get_random_user(Swipe.get_users_list(g.user.id, g.user.friend_radius))
    if next_user_id == 0:
        return redirect('/no-more-swipes')

    return redirect(f'/swipes/{next_user_id}')


@app.route("/swipes/<int:id>", methods=["GET", "POST"])
def swipe_results(id):
    """show swipe pages with buttons and handle results"""

    form = SwipeForm()

    if not g.user:
        flash("Please log in to make friends!")
        return redirect("/")

    swiper = g.user
    swipee = User.query.get_or_404(id)

    if form.validate_on_submit():
        if form.left.data:
            swipe_result = Swipe(
                swiper_id=swiper.id,
                swipee_id=swipee.id,
                swipe_direction='left'
            )
            db.session.add(swipe_result)

        elif form.right.data:
            swipe_result = Swipe(
                swiper_id=swiper.id,
                swipee_id=swipee.id,
                swipe_direction='right'
            )
            db.session.add(swipe_result)

            # check for match
            if (Swipe.check_for_match(swiper_id=swiper.id, swipee_id=swipee.id)):
                Match.make_match(swiper_id=swiper.id, swipee_id=swipee.id)
                flash("you have a match!!!", "success")

        db.session.commit()

        # Filters all users down to just swipable users(i.e. not swiped already and not user)
        next_user_id = get_random_user(Swipe.get_users_list(swiper.id, g.user.friend_radius)
)
        if next_user_id == 0:
            return redirect('/no-more-swipes')

        return redirect(f'/swipes/{next_user_id}')

    return render_template("matching/swipes.html",
                           swipee=swipee,
                           form=form)

@app.get("/no-more-swipes")
def no_swipes():

    return render_template('matching/no_more_swipes.html')

##############################################################################
# Message routes:

@app.get("/messages")
def get_all_messages():
    """get all messages for one user"""

    if not g.user:
        flash("Please log in to view messages!")
        return redirect("/")

    messages_sent, messages_received = g.user.get_message()

    senders = {message.sender for message in messages_received}
    receivers = {message.receiver for message in messages_sent}

    all_conversants = senders | receivers

    user_matches = g.user.get_matches()

    return render_template("matching/messages_all.html",
                           conversants=all_conversants,
                           user_matches=user_matches)


@app.post("/messages")
def go_to_user_page():
    """processes form info and redirect to user messages"""

    match_id = request.form['matches_id']
    match = Match.query.get(match_id)

    user_id = match.user2_id if match.user1_id == g.user.id else match.user1_id

    return redirect(f"/messages/{user_id}")


@app.get("/messages/<int:id>")
def get_conversation(id):
    """get a conversation between user and another user"""

    if not g.user:
        return redirect('/')

    form = NewMessageForm()
    conversant = User.query.get_or_404(id)

    messages_received = Message.query.filter_by(sender_id = id, receiver_id =g.user.id).order_by(desc(Message.timestamp)).all()
    messages_sent = Message.query.filter_by(sender_id = g.user.id, receiver_id =id).order_by(desc(Message.timestamp)).all()

    messages = messages_received + messages_sent
    sorted_messages = sorted(messages, key=lambda m: m.message_id)

    if not g.user:
        flash("Please log in to view messages!")
        return redirect("/")

    return render_template("matching/message.html",
                           messages=sorted_messages,
                           conversant=conversant,
                           form=form)


@app.post("/messages/<int:id>/new")
def post_message(id):
    """send a new message to user"""

    form = NewMessageForm()

    if form.validate_on_submit:
        new_message = Message(
            sender_id=g.user.id,
            receiver_id=id,
            content=form.content.data
        )
        db.session.add(new_message)
        db.session.commit()

        return redirect(f"/messages/{id}")

    flash("could not send message! please try again")
    return redirect("/messages")

##############################################################################
# Error routes:

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404