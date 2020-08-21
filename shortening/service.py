import random
import re
from typing import List

from flask import request

import settings
from analytics import listeners as analytics_hit_listener
from db.db import Session
from shortening.exceptions import URLNotFound
from shortening.models import URL
from users.models import User


def _store_shortened_url(
        user: User,
        actual_url: str,
        short_token: str,
):
    session = Session()


def _get_base_url():
    regex = re.compile('(https?://.+)/')
    return regex.match(request.base_url)[1]


def _generate_short_token(url: str):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(
        [random.choice(alphabet)
         for _ in range(settings.SHORTENER['LENGTH'])]
    )


def make_url_short(user: User, url: str) -> str:
    short_token = _generate_short_token(url)

    session = Session()

    url = URL(
        user_id=user.id,
        actual_url=url,
        short_token=short_token,
    )

    session.add(url)
    session.commit()

    return short_token


def get_actual_url_for_short_token(short_token: str) -> str:
    """
    :raises: URLNotFound
    """
    session = Session()

    url = session.query(URL).filter_by(
        short_token=short_token,
    ).first()

    if url is None:
        raise URLNotFound()

    return url.actual_url


REDIRECT_EVENT_LISTENERS = [analytics_hit_listener.on_redirect_url]


def dispatch_redirect_event(short_token: str):
    print("dispatching event")

    for listener in REDIRECT_EVENT_LISTENERS:
        listener(short_token=short_token)


def get_urls_by_user(user: User) -> List[URL]:
    session = Session()

    return session.query(URL).filter_by(user_id=user.id).all()
