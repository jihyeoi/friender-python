import random

def random_user_id(available_users):
    '''
    Gets a random user id from available users, returns 0 if no available user
    Takes a list of users, returns an integer. Integer willm be 0 if no available users
    '''
    if len(available_users) == 0:
        return 0

    # Generate a random number between 1 and the total count of users
    random_id = random.choice(available_users)

    return random_id




