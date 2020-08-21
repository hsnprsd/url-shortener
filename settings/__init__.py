import os

MODE = os.environ['MODE']

if MODE == 'development':
    from settings.development import *
elif MODE == 'testing':
    from settings.test import *
