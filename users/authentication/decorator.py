from flask import request

from users.authentication.exceptions import UserNotFound
from users.authentication.service import authenticate


def is_authenticated(f):
    def wrapper(*args, **kwargs):
        try:
            authorization = request.headers['authorization'].split(' ')
        except KeyError:
            return "", 401
        authorization_type = authorization[0]
        token = authorization[1]

        if authorization_type != 'Token':
            return "", 401

        try:
            user = authenticate(token)
        except UserNotFound:
            return "", 401

        return f(user, *args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper
