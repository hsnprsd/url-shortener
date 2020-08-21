import datetime
import json
from typing import (
    Dict,
    List,
    Tuple,
)

from analytics import user_agent
from analytics.models import URLHit
from cache.redis import redis_client
from db.db import Session
from shortening.exceptions import URLNotFound
from shortening.models import URL
from users.models import User


def _get_date_datetime_range(
        date: datetime.date,
) -> Tuple[datetime.datetime, datetime.datetime]:
    from_datetime = datetime.datetime(
        year=date.year,
        month=date.month,
        day=date.day,
    )
    to_datetime = datetime.datetime(
        year=date.year,
        month=date.month,
        day=date.day,
    ) + datetime.timedelta(days=1)

    return from_datetime, to_datetime


def _get_url_by_short_token(short_token: str) -> URL:
    session = Session()
    return session.query(URL).filter_by(short_token=short_token).first()


def _calculate_url_analytics_in_date(url: URL, date: datetime.date):
    from_datetime, to_datetime = _get_date_datetime_range(date)

    session = Session()
    hits = session.query(URLHit).filter(
        URLHit.url == url,
        URLHit.created_at >= from_datetime,
        URLHit.created_at < to_datetime,
    ).all()

    data = {
        'date': date.strftime('%Y-%m-%d'),

        'device_type': {},
        'browser_type': {},
        'total_hits': 0,

        'unique_device_type': {},
        'unique_browser_type': {},
        'unique_hits': 0,
    }

    device_type_seen_ips = {}
    browser_type_seen_ips = {}
    seen_ips = set()
    for hit in hits:
        if hit.device_type not in data['device_type']:
            data['device_type'][hit.device_type] = 0
        data['device_type'][hit.device_type] += 1

        if hit.browser_type not in data['browser_type']:
            data['browser_type'][hit.browser_type] = 0
        data['browser_type'][hit.browser_type] += 1

        data['total_hits'] += 1

        if hit.device_type not in device_type_seen_ips:
            device_type_seen_ips[hit.device_type] = set()
        if hit.ip not in device_type_seen_ips[hit.device_type]:
            if hit.device_type not in data['unique_device_type']:
                data['unique_device_type'][hit.device_type] = 0
            data['unique_device_type'][hit.device_type] += 1

            device_type_seen_ips[hit.device_type].add(hit.ip)

        if hit.browser_type not in browser_type_seen_ips:
            browser_type_seen_ips[hit.browser_type] = set()
        if hit.ip not in browser_type_seen_ips[hit.browser_type]:
            if hit.browser_type not in data['unique_browser_type']:
                data['unique_browser_type'][hit.browser_type] = 0
            data['unique_browser_type'][hit.browser_type] += 1

            browser_type_seen_ips[hit.browser_type].add(hit.ip)

        if hit.ip not in seen_ips:
            data['unique_hits'] += 1
        seen_ips.add(hit.ip)

    return data


cache_key_format = "{url_id}-{date}"


def _store_url_analytics_on_cache(url: URL, date: datetime.date, data: Dict):
    json_data = json.dumps(data)

    redis_client.set(
        name=cache_key_format.format(
            url_id=url.id,
            date=date.strftime('%Y-%m-%d'),
        ),
        value=json_data,
    )


def _get_cached_url_analytics_in_date(url: URL, date: datetime.date):
    json_data = redis_client.get(cache_key_format.format(
        url_id=url.id,
        date=date.strftime('%Y-%m-%d'),
    ))
    if json_data is None:
        return None

    return json.loads(json_data)


def _remove_cached_url_analytics_in_date(url: URL, date: datetime.date):
    redis_client.delete(cache_key_format.format(
        url_id=url.id,
        date=date.strftime('%Y-%m-%d'),
    ))


def _get_url_analytics_in_date(url: URL, date: datetime.date) -> Dict:
    cached_data = _get_cached_url_analytics_in_date(url, date)
    if cached_data is not None:
        return cached_data

    # otherwise, calculate and store analytics
    data = _calculate_url_analytics_in_date(url, date)
    _store_url_analytics_on_cache(url, date, data)

    return data


def _get_url_analytics_in_date_range(
        url: URL,
        from_date: datetime.date,
        to_date: datetime.date,
) -> List:
    data = []

    date = from_date
    while date <= to_date:
        data.append(_get_url_analytics_in_date(url, date))
        date += datetime.timedelta(days=1)

    return data


def get_url_analytics(user: User, short_token: str) -> List:
    url = _get_url_by_short_token(short_token)

    if url is None or url.user.id != user.id:
        raise URLNotFound()

    today = datetime.date.today()

    return _get_url_analytics_in_date_range(
        url=url,
        from_date=today - datetime.timedelta(days=30),
        to_date=today,
    )


def record_hit(url: URL) -> URLHit:
    session = Session()

    hit = URLHit(
        url_id=url.id,
        ip=user_agent.get_request_ip(),
        device_type=user_agent.get_request_device_type(),
        browser_type=user_agent.get_request_browser_type(),
    )

    session.add(hit)
    session.commit()

    return hit
