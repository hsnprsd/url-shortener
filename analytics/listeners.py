from analytics.models import URLHit
from analytics.service import record_hit, _remove_cached_url_analytics_in_date
from db.db import Session
from shortening.models import URL


def _expire_url_analytics_cache(hit: URLHit):
    _remove_cached_url_analytics_in_date(
        url=hit.url,
        date=hit.created_at.date(),
    )


URL_HIT_LISTENERS = [_expire_url_analytics_cache]


def dispatch_url_hit_event(hit: URLHit):
    for listener in URL_HIT_LISTENERS:
        listener(hit=hit)


def on_redirect_url(short_token: str):
    session = Session()

    url = session.query(URL).filter_by(short_token=short_token).first()
    if url is None:
        pass

    hit = record_hit(url)

    dispatch_url_hit_event(hit)
