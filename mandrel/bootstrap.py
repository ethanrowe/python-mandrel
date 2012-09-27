import logging.config
import os
import sys
from mandrel import config
from mandrel import exception
from mandrel import util

__BOOTSTRAP_BASENAME = 'Mandrel.py'

LOGGING_CONFIG_BASENAME = 'logging.cfg'
DEFAULT_LOGGING_LEVEL = logging.INFO
DEFAULT_LOGGING_FORMAT = '%(asctime)s.%(msecs)04d #%(process)d - %(levelname)s %(name)s: %(message)s'
DEFAULT_LOGGING_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
__DEFAULT_SEARCH_PATHS = ['.']
_LOGGING_CONFIGURED = False

def logging_is_configured():
    """Returns True if logging has been configured, False if not."""
    return _LOGGING_CONFIGURED

def initialize_simple_logging():
    """The default logging configuration callback.

    Uses `logging.basicConfig` to set up python's logging
    subsystem, using:
        DEFAULT_LOGGING_FORMAT: as the format
        DEFAULT_LOGGING_DATE_FORMAT: as the format for asctime
        DEFAULT_LOGGING_LEVEL: as the logging level threshold

    Override those in your `Mandrel.py` bootstrap file to
    customize this.
    """
    logging.basicConfig(format=DEFAULT_LOGGING_FORMAT,
                        datefmt=DEFAULT_LOGGING_DATE_FORMAT,
                        level=DEFAULT_LOGGING_LEVEL)

def find_logging_configuration():
    """Returns the path to the logging configuration file.

    Searches the SEARCH_PATHS for a file of basename LOGGING_CONFIG_BASENAME.
    Customize these in your `Mandrel.py` bootstrap file to exercise control
    over this.

    Returns the first match found.

    Raises an UnknownConfigurationException if no config file is found.
    """
    for path in util.find_files(LOGGING_CONFIG_BASENAME, SEARCH_PATHS, matches=1):
        return path
    raise exception.UnknownConfigurationException, "Cannot find logging configuration file(s) '%s'" % LOGGING_CONFIG_BASENAME

DEFAULT_LOGGING_CALLBACK = initialize_simple_logging
DISABLE_EXISTING_LOGGERS = True

def configure_logging():
    """Configures the `logging` subsystem.

    This makes a best effort to configure the logging system.
    It first looks for a logging configuration file using `find_logging_configuration`,
    and if found, applies it with `logging.config.fileConfig`.

    If no logging configuration is found, the `DEFAULT_LOGGING_CALLBACK` is called,
    which by default is set to `initialize_simple_logging`.

    After this, the logging system is considered "configured", such that
    `logging_is_configured()` will return True.

    The intention is to guarantee some reasonable logging configuration regardless
    of configuration files available.  You can change the various settings
    in your `Mandrel.py` bootstrap file, and in so doing can exercise control over
    the standard behavior.

    Key settings:
        `DISABLE_EXISTING_LOGGERS`: indicates whether or not the configuration of logging
            via configuration file should disable existing loggers.  Defaults to True.
        `DEFAULT_LOGGING_CALLBACK`: is the callable invoked in the case that no logging
            configuration is found.  By default, `initialize_simple_logging`.

    Note that the `get_logger()` function calls `configure_logging()` as needed,
    and therefore ensures that logging configuration is applied.
    """

    try:
        path = find_logging_configuration()
        logging.config.fileConfig(path, disable_existing_loggers=DISABLE_EXISTING_LOGGERS)
    except exception.UnknownConfigurationException:
        DEFAULT_LOGGING_CALLBACK()
    global _LOGGING_CONFIGURED
    _LOGGING_CONFIGURED = True

def get_logger(name=None):
    """Returns a logger of the specified name, configuring logging if needed.

    If logging is not yet configured, this will attempt to do so via
    `configure_logging`.

    It is recommended that components use this function (or wrappers around it,
    such as those in `mandrel.config.Configuration`) to retrieve logs, rather
    than going to the `logging` module directly.  This ensures that Mandrel
    applies its configuration to logging before logging is initialized.
    """
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
    """Returns path with '~' expanded and relative paths made absolute based on ROOT_PATH."""
    return os.path.realpath(os.path.join(ROOT_PATH, os.path.expanduser(path)))

def parse_bootstrap_file():
    """Compiles and evals the BOOTSTRAP_FILE with controlled local scope.

    The BOOTSTRAP_FILE will be evaluated with the following local
    bindings:
        bootstrap: refers to mandrel.bootstrap
        config: refers to mandrel.config

    This makes it easy for the BOOTSTRAP_FILE to configure mandrel settings
    without performing further imports.
    """
    with open(BOOTSTRAP_FILE, 'rU') as source:
        code = compile(source.read(), BOOTSTRAP_FILE, 'exec')
        eval(code, {'bootstrap': sys.modules[__name__], 'config': config})

(ROOT_PATH, BOOTSTRAP_FILE) = _find_bootstrap_base()
SEARCH_PATHS = util.TransformingList(normalize_path)
SEARCH_PATHS.extend(__DEFAULT_SEARCH_PATHS)
parse_bootstrap_file()

