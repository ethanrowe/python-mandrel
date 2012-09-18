import os

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


