import hashlib
from os import urandom
import string

def make_salt():

    return str(urandom(12))

def make_pw_hash(password, salt=None):

    if not salt:
        salt = make_salt()
    
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return f"{hash},{salt}"

def check_pw_hash(password, hash):

    salt = hash.split(',')[1]
    if make_pw_hash(password, salt) == hash:
        return True
    
    return False