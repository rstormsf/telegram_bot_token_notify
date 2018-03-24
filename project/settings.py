MONGODB = {
    'connection': {},
    'dbname': 'gambit_bot',
}

try:
    from project.settings_local import *
except ImportError:
    pass
