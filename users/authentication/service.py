from typing import TypedDict

from users.authentication.exceptions import UserNotFound
from users.authentication.token import generate_token, get_token_payload
from db.db import Session
from users.models import User


class JWTTokenPayload(TypedDict):
    username: str


def login(username: str, password: str) -> str:
    """
    :return: jwt token

    :raises: UserNotFound
    """

    session = Session()

    user = session.query(User).filter_by(
        username=username,
        password=password,
    ).first()

    if user is None:
        raise UserNotFound()

    return generate_token(JWTTokenPayload(username=username))


def authenticate(token: str) -> User:
    session = Session()

    payload = get_token_payload(token)
    username = payload['username']

    user = session.query(User).filter_by(username=username).first()
    if user is None:
        raise UserNotFound()

    return user
