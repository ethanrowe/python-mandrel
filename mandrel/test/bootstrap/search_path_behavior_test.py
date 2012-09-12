import unittest
import mock
import mandrel
from mandrel.test import utils
import os

class TestSearchPathBehavior(utils.TestCase):
    @mock.patch('mandrel.util.TransformingList')
    def testTargetedListStructure(self, mock_list):
        with utils.bootstrap_scenario() as spec:
            mock_list.return_value.__iter__ = mock.Mock()
            mock_list.return_value.__iter__.return_value = iter(['foo'])
            utils.refresh_bootstrapper()
            # Verify that we're using the normalize_path as a transform function on a transforming list
            mock_list.assert_called_once_with(mandrel.bootstrap.normalize_path)
            self.assertIs(mock_list.return_value, mandrel.bootstrap.SEARCH_PATHS)

    def testNormalizeRelativePath(self):
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            p1 = 'foo'
            p2 = os.path.join('bar', 'baz', 'blee')
            p3 = '.'
            paths = [mandrel.bootstrap.normalize_path(p) for p in (p1, p2, p3)]
            expect = [os.path.realpath(os.path.join(spec[0], p)) for p in (p1, p2, p3)]
            self.assertEqual(expect, paths)

    def testNormalizeAbsolutePath(self):
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            with utils.tempdir() as root:
                paths = [os.path.join(root, x) for x in ('blibby', 'blooby', 'blobby')]
                self.assertEqual(paths, [mandrel.bootstrap.normalize_path(p) for p in paths])

    def testNormalizeUserPath(self):
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            paths = ['~', os.path.join('~', 'fooey')]
            expect = [os.path.realpath(os.path.expanduser(p)) for p in paths]
            self.assertEqual(expect, [mandrel.bootstrap.normalize_path(p) for p in paths])

