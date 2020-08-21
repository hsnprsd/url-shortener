import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from db.db import Base
from shortening.models import URL


class URLHit(Base):
    __tablename__ = 'urls_hits'

    id = Column(Integer, primary_key=True)

    url_id = Column(Integer, ForeignKey('urls.id'), nullable=False)
    url = relationship('URL', back_populates='hits')

    ip = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    browser_type = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.now)


URL.hits = relationship('URLHit', back_populates='url')
