from sqlalchemy.exc import IntegrityError

from db.db import Session
from users.exceptions import UserAlreadyExists
from users.models import User


def register(username: str, password: str):
    session = Session()

    try:
        user = User(
            username=username,
            password=password,
        )
        session.add(user)
        session.commit()
    except IntegrityError:
        raise UserAlreadyExists()
