import os
import re

class TransformingList(object):
    __slots__ = ('_list', '_transformer')

    def __init__(self, transformer):
        self._list = []
        self._transformer = transformer

    def __setitem__(self, i, y):
        self._list[i] = self._transformer(y)

    def __setslice__(self, i, j, y):
        self._list[i:j] = (self._transformer(v) for v in y)

    def __getitem__(self, i):
        return self._list[i]

    def __delslice__(self, i, j):
        del self._list[i:j]

    def __delitem__(self, i):
        del self._list[i]

    def __len__(self):
        return len(self._list)

    def __contains__(self, v):
        return self._transformer(v) in self._list

    def append(self, x):
        self._list.append(self._transformer(x))

    def extend(self, i):
        self._list.extend(self._transformer(x) for x in i)

    def insert(self, i, v):
        self._list.insert(i, self._transformer(v))

    def pop(self, i):
        return self._list.pop(i)

    def count(self, v):
        return self._list.count(self._transformer(v))

def find_files(name_or_names, paths, matches=None):
    """Flexible file locator.

    Looks for files with basename in name_or_names (which
    can be a single string or an ordered container of strings).

    Searches for those files in order across paths in order,
    yielding at most one match per paths entry.

    Exits after matches files have been found.  If matches is
    undefined or less than zero, matches across all paths are
    found.

    Note that it's always restricted to one matching name_or_names
    per path; you do not get all possible matches.

    Parameters:
        name_or_names: a string or ordered container of strings
            corresponding to a prioritized list of file basenames
            to look for.
        dirs: a sequence of paths (directories) that are search for
            name_or_names (in order).
        matches: the limit on the number of matches.

    The function is a generator, so the result is iterable.  Each
    yielded value is the full path to a matching file.
    """

    if isinstance(name_or_names, basestring):
        name_or_names = [name_or_names]

    if matches is None:
        matches = -1

    for path in paths:
        if matches == 0:
            break

        for name in name_or_names:
            target = os.path.join(path, name)
            if os.path.isfile(target):
                yield target
                matches -= 1
                break

def class_to_fqn(cls):
    """Returns the fully qualified name for cls"""
    return '%s.%s' % (cls.__module__, cls.__name__)

def object_to_fqn(obj):
    """Returns the fully qualified name for the class of obj"""
    return class_to_fqn(type(obj))

def get_by_fqn(fqn):
    """Returns the object referred to by fully-qualified name fqn"""
    names = fqn.split('.')
    import_name = names.pop(0)
    thingy = __import__(import_name)
    for name in names:
        import_name += '.%s' % name
        thingy = _lookup(thingy, name, import_name)
    return thingy

def _lookup(module, name, import_name):
    try:
        return getattr(module, name)
    except AttributeError:
        __import__(import_name)
        return getattr(module, name)

def convention_loader(format_string):
    """Returns a function that can dynamically load structures by naming convention.

    An example is most helpful:
        loader = convention_loader('farm.critters.deluxe.%s_animal')
        cowie = loader('moo')
        assert cowie is sys.modules['farm.critters.deluxe.moo_animal']

    This is helpful if you want to use lazy-loading techniques that enforce
    particular naming conventions.

    Parameters:
        format_string: A format string containing a fully qualified python name,
           with a "%s" for where varying names should be substituted.

    Returns:
        A function that can accept a single string argument which, using `get_by_fqn`,
        will return the structure referred to by the result of substituting the
        string into the format_string.

    Raises a TypeError if the format_string is blank, or if the format_string does
    not contain one and only one '%s' within it.
    """
    if not format_string:
        raise TypeError, 'format_string cannot be blank'
    if re.findall('%.', format_string) != ['%s']:
        raise TypeError, 'format_string must contain one and only one "%s" token'

    def func(name):
        return get_by_fqn(format_string % name)

    func.__doc__ = "Returns python structure named by name formatted by %s." % format_string
    func.__name__ = 'formatted_convention_loader'

    return func


def harness_loader(loader_callable):
    """Constructs functions for dynamic loading and callback invocation.

    Example:
        @harness_loader(convention_loader('app.plugins.%s_widget.Widget'))
        def harness(widget_cls, name):
            return widget_cls(name)

    In the example, this:
        x = harness('foo', 'Fooey!')

    is roughly equivalent to, but less sucky for some workflows than, this:
        import app.plugins.foo_widget
        x = app.plugins.foo_widget.Widget('Fooey!')

    This lets you specify a loader_callable that knows how to take a name
    and load something with it, and provide a callback function that does
    something with that loaded thing along with arbitrary parameters.  You
    get a function that puts it all together, so it becomes easy to write
    dynamic loader functions that enforce naming conventions, enforce a
    common interface for pulling structures into a framework (hence the
    name "harness_loader"), etc.

    Parameters:
        loader_callable: a callable thing that can take a single parameter and
            return some arbitrary structure which you want your "harness" to
            consume in some standard way.

    Returns:
        A function that looks like:

        Parameters:
            callback: a callable that you want to invoke on the result
               of the loader_callable invocation.

        Returns:
            A function that looks like:
                Parameters:
                    name: the name of the thing to load via the loader_callable.
                    *args: any positional arguments to pass through to the callback.
                    *kw: any keyword arguments to pass through to the callback.
                
                Returns:
                    The result of invoking the callback with the loaded item,
                    *args, and *kw.
    """
    def harness_builder(callback):
        def harness(name, *args, **kw):
            target = loader_callable(name)
            return callback(target, *args, **kw)
        return harness
    return harness_builder

