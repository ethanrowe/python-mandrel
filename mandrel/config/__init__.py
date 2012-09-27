from mandrel.config import core
import sys

__all__ = ['find_configuration_files',
           'find_configuration_file',
           'load_configuration_file',
           'get_configuration',
           'Configuration',
           'ForgivingConfiguration']

for name in __all__:
    setattr(sys.modules[__name__], name, getattr(core, name))

