import os
import sys
from mandrel import config
from mandrel import exception
from mandrel import util

__BOOTSTRAP_BASENAME = 'Mandrel.py'

LOGGING_CONFIG_BASENAME = 'logging.cfg'
__DEFAULT_SEARCH_PATHS = ['.']

def _find_bootstrap_base():
    current = os.path.realpath('.')
    while not os.path.isfile(os.path.join(current, __BOOTSTRAP_BASENAME)):
        parent = os.path.dirname(current)
        if parent == current:
            raise exception.MissingBootstrapException, 'Cannot find %s file in directory hierarchy' % __BOOTSTRAP_BASENAME
        current = parent

    return current, os.path.join(current, __BOOTSTRAP_BASENAME)

def normalize_path(path):
    return os.path.realpath(os.path.join(ROOT_PATH, os.path.expanduser(path)))

def parse_bootstrap_file():
    with open(BOOTSTRAP_FILE, 'rU') as source:
        code = compile(source.read(), BOOTSTRAP_FILE, 'exec')
        eval(code, {'bootstrap': sys.modules[__name__], 'config': config})

(ROOT_PATH, BOOTSTRAP_FILE) = _find_bootstrap_base()
SEARCH_PATHS = util.TransformingList(normalize_path)
SEARCH_PATHS.extend(__DEFAULT_SEARCH_PATHS)
parse_bootstrap_file()

