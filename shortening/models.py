from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.db import Base
from users.models import User


class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='urls')

    actual_url = Column(String, nullable=False)
    short_token = Column(String, nullable=False, unique=True)


User.urls = relationship('URL', back_populates='user')
