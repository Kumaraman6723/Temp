import random
from werkzeug.security import check_password_hash

def otpmaker():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

def check_password(hashed_password, user_password):
    return check_password_hash(hashed_password, user_password)
