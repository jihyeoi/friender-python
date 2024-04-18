import random
from models import User
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def user_count():
    total_users = User.query.count()
    return total_users

def random_user_id():
    total_users = user_count()
    # Generate a random number between 1 and the total count of users
    random_id = random.randint(1, total_users)
    return random_id