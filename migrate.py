from db.db import engine

from users.models import *
from shortening.models import *
from analytics.models import *


def migrate():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    migrate()
