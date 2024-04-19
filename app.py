import os
from dotenv import load_dotenv
from flask import ( Flask, render_template, flash, redirect, session, g )
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
import boto3

from forms import ( CSRFProtection, SignupForm, LoginForm, NewMessageForm, SwipeForm )
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
        print('$$$$$$$$$$$$$$$$$$$$$$$ curr user key in session')

    else:
        print('$$$$$$$$$$$$$$$$$$$$$$$ curr user key NOT in session')
        g.user = None


@app.before_request
def add_csrf_only_form():
    """Add a CSRF-only form so that every route can use it."""

    g.csrf_form = CSRFProtection()


def do_login(user):
    """Log in user."""

    print('$$$$$$$$$$$$$$$$$$$$$$$ doing login')
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    print('$$$$$$$$$$$$$$$$$$$$$$$ doing logout')
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
    #TODO: ADD RADIUS but later
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
                interests=form.interests.data,
                friend_radius=form.friend_radius.data
            )
            print("username in signup is", user.username)
            db.session.commit()
            print("it hit the commit")

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
    print('$$$$$$$$$$$$$$$$$$$$$$$ g.user', g.user)
    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()
    print('$$$$$$$$$$$$$$$$$$$$$$$ after do_logut')
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
    return render_template("profile.html")


##############################################################################
# Swipe routes:

@app.post("/swipes/new")
def redirect_to_swipes():
    """landing page for swiping"""
    # TODO: need logic here
    # get random id from avail users
    # redirect to swipes id

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
    # TODO: include second param of num_miles for radius check

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
                flash("you have a match!!!", "success")
            print("Swiped right", form.right.data)

        db.session.commit()

        # Filters all users down to just swipable users(i.e. not swiped already and not user)
        # Allows for endless(?) swiping of available users
        # If no more avaiable users to swipe, renders no more friends page

        next_user_id = get_random_user(Swipe.get_users_list(swiper.id, g.user.friend_radius)
)
        if next_user_id == 0:
            print('############ redirecting to no more swipes')
            return redirect('/no-more-swipes')

        return redirect(f'/swipes/{next_user_id}')

    return render_template("swipes.html",
                           swipee=swipee,
                           form=form)

@app.route("/no-more-swipes", methods=["GET", "POST"])
def no_swipes():

    return render_template('no_more_swipes.html')

##############################################################################
# Message routes:

@app.get("/messages")
def get_all_messages():
    """get all messages for one user"""

    if not g.user:
        flash("Please log in to view messages!")
        return redirect("/")

    # all messages sent by user
    messages_sent = Message.query.filter_by(sender_id = g.user.id).all()
    # all messages rcvd by user
    messages_received = Message.query.filter_by(receiver_id = g.user.id).all()
    # TODO: also need to check for messages received from others
    # g.user may not have responded to messages, need to check both in and out

    senders = {message.sender for message in messages_received}
    receivers = {message.receiver for message in messages_sent}

    all_conversants = senders | receivers

    print('senders', senders)
    print('receivers', receivers)
    print('all_conversants', all_conversants)

    # message.receiver.first_name
    # print("USER ID :", g.user.id)
    # print("MESSAGES!!!!", messages)
    # order by sent_at
    # declare a most recent variable
    # loop over the messages
    # update the variable whenever we find a more recent message

    return render_template("messages_all.html", conversants=all_conversants)

@app.get("/messages/<int:id>")
def get_conversation(id):
    """get a conversation between user and another user"""

    if not g.user:
        return redirect('/')

    form = NewMessageForm()
    conversant = User.query.get_or_404(id)

    messages_received = Message.query.filter_by(sender_id = id, receiver_id =g.user.id).order_by(desc(Message.timestamp)).all()
    messages_sent = Message.query.filter_by(sender_id = g.user.id, receiver_id =id).order_by(desc(Message.timestamp)).all()
    print('messages_received', messages_received)
    print('messages_sent', messages_sent)

    messages = messages_received + messages_sent
    print('messages', messages)
    sorted_messages = sorted(messages, key=lambda m: m.message_id)

    print('sorted_messages', sorted_messages)
    if not g.user:
        flash("Please log in to view messages!")
        return redirect("/")
    # get all messages sent from and to conversant(id)
    # messages = Message.query.filter_by(sender_id = g.user.id).all()
    # receivers = {message.receiver for message in messages}


    return render_template("conversation.html",
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

        print("NEW MESSAGE", new_message.content)

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