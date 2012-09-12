import logging.config
import os
import sys
from mandrel import config
from mandrel import exception
from mandrel import util

__BOOTSTRAP_BASENAME = 'Mandrel.py'

LOGGING_CONFIG_BASENAME = 'logging.cfg'
__DEFAULT_SEARCH_PATHS = ['.']
_LOGGING_CONFIGURED = False

def logging_is_configured():
    return _LOGGING_CONFIGURED

def initialize_simple_logging():
    logging.basicConfig(level=logging.DEBUG)

def find_logging_configuration():
    for path in util.find_files(LOGGING_CONFIG_BASENAME, SEARCH_PATHS, matches=1):
        return path
    raise exception.UnknownConfigurationException, "Cannot find logging configuration file(s) '%s'" % LOGGING_CONFIG_BASENAME

DEFAULT_LOGGING_CALLBACK = initialize_simple_logging
DISABLE_EXISTING_LOGGERS = True

def configure_logging():
    try:
        path = find_logging_configuration()
        logging.config.fileConfig(path, disable_existing_loggers=DISABLE_EXISTING_LOGGERS)
    except exception.UnknownConfigurationException:
        DEFAULT_LOGGING_CALLBACK()
    global _LOGGING_CONFIGURED
    _LOGGING_CONFIGURED = True

def get_logger(name=None):
    if not logging_is_configured():
        configure_logging()
    return logging.getLogger(name)


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

