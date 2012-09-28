import mandrel
from mandrel import exception
from mandrel import util
import yaml

def _get_bootstrapper():
    if not hasattr(mandrel, 'bootstrap'):
        __import__('mandrel.bootstrap')
    return mandrel.bootstrap

def read_yaml_path(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

LOADERS = [('yaml', read_yaml_path)]

def get_possible_basenames(name):
    """Calculates possible configuration file basenames for a root name.

    A name 'foo' could correspond to a configuration file with any
    of the extensions we have registered in LOADERS.  When searching for
    a configuration file, we consider all possible extensions based on
    what LOADERS tells us we can understand.

    Therefore, with LOADERS of [('yaml', a_yamler), ('json', a_jsoner)],
    get_possible_basenames('foo') --> ['foo.yaml', 'foo.json'].

    Note, however, that if name already has an extension that matches
    one that we understand, we simply pass through the name.  Thus,
    get_possible_basenames('foo.json') --> ['foo.json'] in our example.

    Parameters:
        name: a string representing a configuration file basename, typically
            without an extension.

    Returns an array of all variations of that file basename we would be able
    to load given the extension/loader map we have in LOADERS (with exception
    noted above in the case that the name already matches one of our extensions).
    """
    matches = []
    for ext, reader in LOADERS:
        end = '.' + ext
        if name[-len(end):] == end:
            return [name]
        matches.append(name + end)

    return matches

def find_configuration_files(name):
    """Finds readable configuration files across config.bootstrap.SEARCH_PATHS for name.

    Using get_possible_basenames() to determine possible file basenames for name,
    looks across directories in config.bootstrap.SEARCH_PATHS and yields each
    highest-priority (according to extension order in LOADERS) existing config file
    within SEARCH_PATHS.

    Parameters:
        name: a string representing a configuration file basename, typically
            without an extension.

    Yields each existing best match across directories in SEARCH_PATHS.  The yielded paths
    are full, absolute paths.
    """
    return util.find_files(get_possible_basenames(name), _get_bootstrapper().SEARCH_PATHS)

def find_configuration_file(name):
    """Finds the highest-priority readable configuration file for name.

    Provides same logic/rules as find_configuration_files(name), except that:
    * it will return only the highest-priority result
    * it will throw an UnknownConfigurationException if no file can be found.

    Parameters:
        name: a string representing a configuration file basename, typically
            without an extension.

    Returns the full string path to the best matching configuration file across the
    SEARCH_PATHS, based on extension order in LOADERS.

    Throws an UnknownConfigurationException if no such file exists.
    """
    for path in find_configuration_files(name):
        return path
    raise exception.UnknownConfigurationException, "No configuration file found for name '%s'" % name

def get_loader(path):
    """Gets the configuration loader for path according to file extension.

    Parameters:
        path: the path of a configuration file, including the filename
            extension.

    Returns the loader associated with path's extension within LOADERS.

    Throws an UnknownConfigurationException if no such loader exists.
    """
    for ext, loader in LOADERS:
        fullext = '.' + ext
        if path[-len(fullext):] == fullext:
            return loader
    raise exception.UnknownConfigurationException, "No configuration loader found for path '%s'" % path

def load_configuration_file(path):
    """Loads the configuration at path and returns it.

    Parameters:
        path: the path to the configuration file to load.

    Returns the dictionary resulting from loading the specified configuration file.
    """
    loader = get_loader(path)
    return loader(path)

def get_configuration(name):
    """Finds and loads the best configuration for name.

    Looks for configuration files for name valid for LOADERS
    across the directories specified in mandrel.bootstrap.SEARCH_PATHS.

    If one is found, uses the loader appropriate for the configuration
    file extension to load that file into a dictionary, and returns it.

    Parameters:
        name: the name of the configuration file to look for and load,
            typically without an extension.

    Returns the dictionary resulting from loading the located file.

    May throw an UnknownConfigurationException if no file can be found,
    or if the file has no loader.  May also throw other exceptions
    according to the loader used.
    """
    return load_configuration_file(find_configuration_file(name))

class Configuration(object):
    """Base class for managing component configuration.

    Configuration provides:
    * Simple wrapper around mandrel.config functionality for locating
      and loading configuration from files.
    * Easy, minimal interface for working with configuration as python
      objects rather than dictionaries.
    * Easy domain-specific configuration subclassing with minimal
      fuss.
    * Composable design to give flexibility in how configuration is shared
      between/across components.

    Extend this class and override NAME in order to get automatic
    loading and log configuration.

    If you want a class that provides a full range of defaults such that
    it could function in the complete absence of configuration input,
    consider extending ForgivingConfiguration instead.

    By default, when getting an attribute, if the attribute does not
    exist on the instance, it is looked for (as a key) within the
    instance's configuration dictionary.  If not found there, the
    objects in the instance's chain are checked for the attribute
    in turn.

    When setting an attribute on an instance, the effect is to set
    that attribute on the underlying configuration dictionary (as
    a key/value pair), rather than on the instance itself.
    """
    NAME = None

    @classmethod
    def load_configuration(cls):
        """Returns the best configuration dictionary available for the class.

        Uses the class constant NAME as the name lookup for the configuration
        file.

        Note that this *always* goes to the file system for configuration; no
        caching takes place.  Manage your own state in the manner best suited
        to your problem domain.

        Raises an UnknownConfigurationException if no such configuration can
        be found.  Additionally, since configuration depends on bootstrapping,
        this is subject to any exceptions bootstrapping may bring.
        """
        return get_configuration(cls.NAME)

    @classmethod
    def get_configuration(cls, *chain):
        """Returns an instance prepped with the best configuration available.

        The instance returned will use the configuration dictionary found via
        get_configuration, and will have the specified chain.

        Raises an UnknownConfigurationException is no such configuration can
        be found.  Additionally, since configuration depends on bootstrapping,
        this is subject to any exceptions bootstrapping may bring.
        """
        return cls(cls.load_configuration(), *chain)

    @classmethod
    def get_logger(cls, name=None):
        """Returns a logger according to the class' constant NAME.

        This uses the mandrel.bootstrap.get_logger() functionality
        to work nicely within the bootstrapping and logging configuration
        design.

        The logger name requested is always relative to the class'
        constant NAME; if you do not provide a name, then you'll get
        the result of mandrel.bootstrap.get_logger(cls.NAME).
        If you provide a name, it will be treated as a child of
        that name.  So that name "foo" will get the result of
        mandrel.bootstrap.get_logger('%s.foo' % cls.NAME)

        Note that the logger is always retrieved from the logging subsystem;
        no caching is performed within the Configuration class itself.

        This is subject to any exceptions that bootstrapping itself
        is subject to.
        """
        if name:
            name = '%s.%s' % (cls.NAME, name)
        else:
            name = cls.NAME
        return _get_bootstrapper().get_logger(name)

    def __init__(self, configuration, *chain):
        """Initialize the object with a configuration dictionary and any number of chain members."""
        self.instance_set('configuration', configuration)
        self.instance_set('chain', tuple(chain))

    def configuration_set(self, attribute, value):
        """Sets the attribute and value as a key,value pair on the configuration dictionary."""
        self.configuration[attribute] = value

    def configuration_get(self, attribute):
        """Retrieves the requested attribute (as a key) from the configuration dictionary."""
        return self.configuration[attribute]

    def instance_set(self, attribute, value):
        """Sets the attribute and value on the instance directly."""
        super(Configuration, self).__setattr__(attribute, value)

    def instance_get(self, attribute):
        """Returns the attribute from the instance directly."""
        return getattr(self, attribute)

    def chained_get(self, attribute):
        """Returns the 'best' value for the attribute, consulting the configuration then the chain in turn."""
        try:
            return self.configuration_get(attribute)
        except KeyError:
            pass

        for item in self.chain:
            try:
                return getattr(item, attribute)
            except AttributeError:
                pass

        raise AttributeError, 'No such attribute: %s' % attribute

    def __getattr__(self, attr):
        return self.chained_get(attr)

    def __setattr__(self, attr, val):
        if hasattr(getattr(self.__class__, attr, None), '__set__'):
            # Descriptor support
            return object.__setattr__(self, attr, val)
        return self.configuration_set(attr, val)

    def hot_copy(self):
        """Returns a new instance of the same class, using self as the first point in the chain.

        That "hot copy" is logically a copy of self, but with a distinct dictionary such that
        mutations to the copy do not affect the original.

        However, because the original exposes its state through chaining, its possible to
        indirectly alter the state of the original configuration.
        """
        return type(self)({}, self)

class ForgivingConfiguration(Configuration):
    """Configuration class for defaults or empty configs.

    If your configuration is such that you can cope with an empty/missing
    configuration, presumably by providing sane defaults, use the ForgivingConfiguration
    instead of Configuration.

    ForgivingConfiguration is identical to its parent class Configuration, except
    that in the event of an UnknownConfigurationException, load_configuration() will
    return an empty dict instead of failing.

    Enforcing reasonable application-specific defaults then is a matter for
    your implementation.
    """

    @classmethod
    def load_configuration(cls):
        """Return the best configuration dictionary available from files.
        
        If no configuration file can be found, an empty dictionary is returned.
        """
        try:
            return super(ForgivingConfiguration, cls).load_configuration()
        except exception.UnknownConfigurationException:
            return {}

