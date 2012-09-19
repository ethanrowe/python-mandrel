import mock
import unittest
import os
import sys
from mandrel import util
from mandrel.test import utils

class TestFQNUtils(unittest.TestCase):
    def testClassToFQN(self):
        mod = str(mock.Mock(name='SomeMockModuleName'))
        name = str(mock.Mock(name='SomeMockClassName'))
        cls = mock.Mock(name='MockClass')
        cls.__module__ = mod
        cls.__name__ = name
        self.assertEqual('%s.%s' % (mod, name), util.class_to_fqn(cls))


    def testObjectToFQN(self):
        cls = type(str(mock.Mock(name='SomeTestingClass')), (object,), {})
        obj = cls()
        self.assertEqual('%s.%s' % (cls.__module__, cls.__name__), util.object_to_fqn(obj))


    def testGetByFQNImportable(self):
        with utils.tempdir() as tmp:
            path = os.path.join(tmp, 'fluffypants')
            os.mkdir(path)
            with open(os.path.join(path, '__init__.py'), 'w') as f:
                f.write("\n")

            with open(os.path.join(path, 'happydance.py'), 'w') as f:
                f.write("\n")

            sys.path.insert(0, tmp)
            try:
                result = util.get_by_fqn('fluffypants.happydance')
                self.assertEqual('fluffypants.happydance', result.__name__)
            finally:
                sys.path.pop(0)


    @mock.patch('mandrel.test.utils')
    def testGetByFQNGettable(self, mock_utils):
        result = util.get_by_fqn('mandrel.test.utils.foofy')
        self.assertEqual(mock_utils.foofy, result)


    def testGetByFQNBadImport(self):
        self.assertRaises(ImportError, lambda: util.get_by_fqn('mandrel.fluffypants'))

