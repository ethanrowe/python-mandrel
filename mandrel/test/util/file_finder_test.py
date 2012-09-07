import contextlib
import mock
import os
import unittest
from mandrel.test import utils
from mandrel import util

@contextlib.contextmanager
def scenario(**files_to_levels):
    levels = []
    with utils.tempdir() as a:
        levels.append(a)
        with utils.tempdir() as b:
            levels.append(b)
            with utils.tempdir() as c:
                levels.append(c)
                for name, dirs in files_to_levels.items():
                    for level in dirs:
                        with open(os.path.join(levels[level], name), 'w') as f:
                            f.write(str(level))

                with utils.bootstrap_scenario() as spec:
                    with mock.patch('mandrel.bootstrap.SEARCH_PATHS', new=levels):
                        yield levels


def get_level(path):
    with open(path, 'r') as f:
        return int(f.read())


class TestFileFinder(unittest.TestCase):
    def testSingleFindOneMatch(self):
        with scenario(**{'a.txt': (0, 1, 2), 'b.foo': (1, 2), 'c.bar': (2,)}) as dirs:
            for name, level in {'a.txt': 0, 'b.foo': 1, 'c.bar': 2}.items():
                result = tuple(util.find_files(name, dirs, matches=1))
                self.assertEqual(1, len(result))
                self.assertEqual(level, get_level(result[0]))

    def testSingleFindTwoMatch(self):
        with scenario(**{'0.x': (0,), 'a.txt': (0, 1, 2), 'b.foo': (1, 2), 'c.bar': (2,)}) as dirs:
            for name, levels in {'0.x': (0,), 'a.txt': (0, 1), 'b.foo': (1, 2), 'c.bar': (2,)}.items():
                got = tuple(get_level(r) for r in util.find_files(name, dirs, matches=2))
                self.assertEqual(levels, got)

    def testSingleFindMultiMatch(self):
        mapping = {'0.x': (0,), 'a.txt': (0, 1), 'b.blah': (0, 1, 2), 'c.pork': (1, 2), 'd.plonk': (1,), 'e.sporks': (2,)}
        with scenario(**mapping) as dirs:
            for name, levels in mapping.items():
                got = tuple(get_level(r) for r in util.find_files(name, dirs))
                self.assertEqual(levels, got)

    def testMultiFind(self):
        normalize = lambda f: (os.path.basename(f), get_level(f))
        with scenario(a=(0, 1, 2), b=(0, 1, 2), c=(1,), d=(0, 2), e=()) as dirs:
            self.assertEqual(
                    [('a', 0), ('a', 1), ('a', 2)],
                    [normalize(r) for r in util.find_files(('a', 'b'), dirs)])
            self.assertEqual(
                    [('b', 0), ('b', 1), ('b', 2)],
                    [normalize(r) for r in util.find_files(('b', 'a'), dirs)])
            self.assertEqual(
                    [('a', 0), ('c', 1), ('a', 2)],
                    [normalize(r) for r in util.find_files(('c', 'a'), dirs)])
            self.assertEqual(
                    [('d', 0), ('c', 1), ('d', 2)],
                    [normalize(r) for r in util.find_files(('e', 'd', 'c', 'a', 'b'), dirs)])

