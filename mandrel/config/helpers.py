from .. import util

def configurable_class(setting_name, default_class_name=None):
    def getter(self):
        value = None
        try:
            value = self.configuration_get(setting_name)
        except KeyError:
            pass

        if not value:
            if not default_class_name:
                return None
            value = default_class_name

        return util.get_by_fqn(value)

    def setter(self, value):
        if value is not None:
            return self.configuration_set(setting_name, util.class_to_fqn(value))
        return self.configuration_set(setting_name, None)

    return property(getter, setter)


def resolve_logger_name(*names):
    return '.'.join(name for name in names if name)

def named_logger(base_name):
    """Returns a classmethod for logger name calculation that uses `base_name` as the top portion.
    
    Ordinarily, the following class:
        
        class Foo(core.Configuration):
            NAME = 'foo'
    
    would produce logger names like:
    
        Foo.get_logger_name() # "foo"
        Foo.get_logger_name('blah') # "foo.blah"
    
    But use the helper in this manner to use an alternate name that you specify:
    
        class Foo(core.Configuration):
            NAME = 'foo'
            get_logger_name = helpers.named_logger('top.fu')
        
    And now the behavior is:
    
        Foo.get_logger_name() # "top.fu"
        Foo.get_logger_name('blah') # "top.fu.blah"
    """
    def get_logger_name(cls, name=None):
        return resolve_logger_name(base_name, name)
    get_logger_name.__doc__ = "Produces a logger name using '%s' as the base portion." % base_name
    return classmethod(get_logger_name)

def templated_name_logger(template):
    """Returns a classmethod that calculates logger names by first applying the class name to `template`.

    For instance:

        class Foo(core.Configuration):
            NAME = 'foo'
            get_logger_name = helpers.templated_name_logger('my.%s')

        class Bar(Foo):
            NAME = 'bar'

        Foo.get_logger_name('blah') # "my.foo.blah"
        Bar.get_logger_name('blah') # "my.bar.blah"
    """
    def get_logger_name(cls, name=None):
        return resolve_logger_name(template % cls.NAME, name)
    get_logger_name.__doc__ = "Produces a logger name merging cls.NAME into '%s' as base portion." % template
    return classmethod(get_logger_name)


def name_chain_logger(chain):
    """Returns a classmethod that determines logger name base by delegating to `chain.get_logger_name(cls.NAME)`.

    This allows for composition of logger names without reliance on inheritance hierarchy:

        class Foo(core.Configuration):
            NAME = 'foo'

        class Bar(core.Configuration):
            NAME = 'bar'
            get_logger_name = helpers.name_chain_logger(Foo)

        class Baz(core.Configuration):
            NAME = 'baz'
            get_logger_name = helpers.name_chain_logger(Bar)

        Foo.get_logger_name('blah') # "foo.blah"
        Bar.get_logger_name('blah') # "foo.bar.blah"
        Baz.get_logger_name('blah') # "foo.bar.baz.blah"
    """
    def get_logger_name(cls, name=None):
        return chain.get_logger_name(resolve_logger_name(cls.NAME, name))
    get_logger_name.__doc__ = "Produces a logger name by composing with %s.get_logger_name" % chain.__name__
    return classmethod(get_logger_name)


def hierarchical_logger(base):
    """Returns a classmethod that chains logger names by walking up the inheritance graph to `base`.

    This facilitates ease of name organization within a given project with multiple configuration classes.

        class App(core.Configuration):
            NAME = 'app'
            get_logger_name = helpers.hierarchical_logger(App)

        class ComponentA(App):
            NAME = 'a'

        class ComponentB(App):
            NAME = 'b'

        class SubComponentX(ComponentB):
            NAME = 'x'

        App.get_logger_name('foo') # "app.foo"
        ComponentA.get_logger_name('foo') # "app.a.foo"
        ComponentB.get_logger_name('foo') # "app.b.foo"
        SubComponentX.get_logger_name('foo') # "app.b.x.foo"
    """
    def get_logger_name(cls, name=None):
        if cls is base:
            return resolve_logger_name(cls.NAME, name)

        classes = cls.__mro__[1:]
        for target_class in classes:
            if hasattr(target_class, 'get_logger_name'):
                return target_class.get_logger_name(resolve_logger_name(cls.NAME, name))

        raise NotImplementedError("The inheritance hierarchy does not support hierarchical get_logger_name().")

    get_logger_name.__doc__ = "Produces a logger name by composing names walking up the hierarchy from cls to %s" % base.__name__
    return classmethod(get_logger_name)

