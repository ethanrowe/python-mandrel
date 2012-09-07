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
