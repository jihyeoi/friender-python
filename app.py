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
from werkzeug.utils import secure_filename
from forms import (CSRFProtection, SignupForm, LoginForm, PhotoForm)
from models import (
    db, connect_db, User, Message, DEFAULT_IMAGE_URL)

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
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                zip_code=form.zip_code.data,
                # TODO: PUT AN UPLOAD FORM HERE
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
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
# General user routes:


##############################################################################
# Picture Upload routes:

# @app.post('/picture')
# def upload_picture():
#     ''' Uploads a picture '''

#     form = PictureUploadForm()
#     if form.validate_on_submit():

#     pic_url = form.url.data

@app.route("/picture", methods=["GET", "POST"])
def upload_file():
    form = PhotoForm()
    print('$$$$$$$$$$$$$$$$ form is', form)
    print('$$$$$$$$$$$$$$$$ form data is', form.photo.data)
    if form.validate_on_submit():
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$ if statement here')
        file = form.photo.data
        filename = secure_filename(file.filename)
        try:
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                filename,
                ExtraArgs={
                    "ContentType": file.content_type
                }
            )
            return redirect(S3_LOCATION + filename)
        except Exception as e:
            print("Something Happened: ", e)
            return redirect(url_for('home'))
    return render_template('picture.html', form=form)
