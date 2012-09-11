class MandrelException(Exception):
    pass

class MissingBootstrapException(MandrelException):
    pass

class UnknownConfigurationException(MandrelException):
    pass
