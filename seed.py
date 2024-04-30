"""Initial data."""

from models import db, User, Swipe, Message, Swipe, Match

from app import app

db.drop_all()
db.create_all()


#######################################
# add users
user1 = User(
    id=2,
    username='anna',
    email='anna@gmail.com',
    zip_code='92501',
    first_name='anna',
    last_name='the dog',
    interests='eating, running, fetching',
    hashed_password="secret",
    photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/dog.jpeg",
    friend_radius=25
)

user2 = User(
    id=3,
    username='tim',
    email='tim@gmail.com',
    zip_code='11565',
    first_name='tim',
    last_name='him',
    interests='nature walks, doing nothing, watching tv',
    hashed_password="secret",
    photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/73eca85c-4c88-438c-aed8-9dd02e3288c4.JPG",
    friend_radius=25
)

user3 = User(
    id=4,
    username='bob',
    email='bob@gmail.com',
    zip_code='92509',
    first_name='bob',
    last_name='bobber',
    interests='online shopping, running, gardening',
    # bob's hashed password equates to 'password'
    hashed_password="$2b$12$oB1GmibCDWzbMfEWzNsjperI2NRbybHAnodeKbNRFdVa6IDUVstnu",
    photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/dog.jpeg",
    friend_radius=25
)

user4 = User(
    id=5,
    username='officeguy',
    email='office@gmail.com',
    zip_code='92507',
    first_name='jim',
    last_name='halpert',
    interests='scheming, pranking people, hanging out with pam',
    hashed_password="secret",
    photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/jim.png",
    friend_radius=25
)

user5 = User(
    id=6,
    username='sherlock',
    email='sher@gmail.com',
    zip_code='92504',
    first_name='sherlock',
    last_name='holmes',
    interests='puzzles, violin, deductive reasoning',
    hashed_password="secret",
    photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/sherlock.png",
    friend_radius=25
)

user6 = User(
    id=7,
    username='ironman',
    email='tony@gmail.com',
    zip_code='92501',
    first_name='tony',
    last_name='stark',
    interests='racing cars, saving the world, designing technology',
    hashed_password="secret",
    photo_url="https://frienderphotosforrithm.s3.us-east-2.amazonaws.com/tony.jpeg",
    friend_radius=25
)

user7 = User(
    id=8,
    username='super-saiyan',
    email='goku@gmail.com',
    zip_code='92501',
    first_name='son',
    last_name='goku',
    interests='martial arts, eating',
    hashed_password="secret",
    photo_url="https://friender-photos-2024.s3.us-east-2.amazonaws.com/goku-dragon-ball-guru-824x490-11b2006-e1697471244240.jpg",
    friend_radius=25
)

user8 = User(
    id=9,
    username='happy-painter',
    email='painterly@gmail.com',
    zip_code='92507',
    first_name='bob',
    last_name='ross',
    interests='painting, teaching, mindfulness',
    hashed_password="secret",
    photo_url="https://friender-photos-2024.s3.us-east-2.amazonaws.com/bobearly1_custom-370196c6c7ccc113e242096bb8e7164e96af78f9.jpg",
    friend_radius=25
)

user9 = User(
    id=10,
    username='rocky',
    email='the_rock@gmail.com',
    zip_code='92506',
    first_name='dwayne',
    last_name='johnson',
    interests='fitness, movies, wrestling',
    hashed_password="$2b$12$oB1GmibCDWzbMfEWzNsjperI2NRbybHAnodeKbNRFdVa6IDUVstnu",
    photo_url="https://friender-photos-2024.s3.us-east-2.amazonaws.com/7fa2f2009d33fcd5_Baywatch_2.webp",
    friend_radius=25
)

swipe1 = Swipe(
    id=100,
    swiper_id=2,
    swipee_id=4,
    swipe_direction='right'
)

swipe2 = Swipe(
    id=101,
    swiper_id=4,
    swipee_id=7,
    swipe_direction='right'
)

swipe3 = Swipe(
    id=102,
    swiper_id=4,
    swipee_id=2,
    swipe_direction='right'
)

swipe4 = Swipe(
    id=103,
    swiper_id=7,
    swipee_id=4,
    swipe_direction='right'
)

match1 = Match(
    match_id = 1,
    user1_id = 4,
    user2_id = 2
)

match2 = Match(
    match_id = 2,
    user1_id = 7,
    user2_id = 4
)

# swipe3 = Swipe(
#     id=102,
#     swiper_id=5,
#     swipee_id=2,
#     swipe_direction='left'
# )

# swipe4 = Swipe(
#     id=103,
#     swiper_id=6,
#     swipee_id=7,
#     swipe_direction='right'
# )

# swipe5 = Swipe(
#     id=104,
#     swiper_id=9,
#     swipee_id=10,
#     swipe_direction='right'
# )

# swipe6 = Swipe(
#     id=105,
#     swiper_id=10,
#     swipee_id=9,
#     swipe_direction='right'
# )

# swipe7 = Swipe(
#     id=106,
#     swiper_id=10,
#     swipee_id=8,
#     swipe_direction='right'
# )

# swipe8 = Swipe(
#     id=107,
#     swiper_id=8,
#     swipee_id=10,
#     swipe_direction='right'
# )

message1 = Message(
    message_id = 100,
    sender_id = 4,
    receiver_id=2,
    content="should be 1st"
)

message2 = Message(
    message_id = 101,
    sender_id = 3,
    receiver_id=4,
    content="should be 2nd"
)

# message3 = Message(
#     message_id = 102,
#     sender_id = 2,
#     receiver_id=4,
#     content="gotta be 3rd"
# )

# message4 = Message(
#     message_id = 104,
#     sender_id = 6,
#     receiver_id=4,
#     content="hey you"
# )

# message5 = Message(
#     message_id = 105,
#     sender_id = 4,
#     receiver_id=7,
#     content="is it true that you know the hulk"
# )

# message6 = Message(
#     message_id = 106,
#     sender_id = 4,
#     receiver_id=6,
#     content="I have a mystery for you... "
# )

# message7 = Message(
#     message_id = 107,
#     sender_id = 6,
#     receiver_id=4,
#     content="Sorry, I'm on vacation. I'll get back to you in a few days"
# )

# message8 = Message(
#     message_id = 108,
#     sender_id = 8,
#     receiver_id=4,
#     content="Want to train together?"
# )

# message9 = Message(
#     message_id = 109,
#     sender_id = 10,
#     receiver_id=8,
#     content="You know it"
# )

# message10 = Message(
#     message_id = 110,
#     sender_id = 10,
#     receiver_id=4,
#     content="Up for a workout?"
# )

# message11 = Message(
#     message_id = 111,
#     sender_id = 4,
#     receiver_id=10,
#     content="No thanks"
# )

# message12 = Message(
#     message_id = 112,
#     sender_id = 9,
#     receiver_id=10,
#     content="But if you want to learn to paint..."
# )

db.session.add_all([user1, user2, user3, user4, user5, user6, user7, user8, user9])
db.session.commit()
db.session.add_all([swipe1, swipe2, swipe3, swipe4])
db.session.commit()
db.session.add_all([message1, message2])
db.session.commit()
db.session.add_all([match1, match2])
db.session.commit()


