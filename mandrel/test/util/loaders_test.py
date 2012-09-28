import unittest
import mock
from mandrel import util

class TestLoaderFunctions(unittest.TestCase):
    @mock.patch.object(util, 'get_by_fqn')
    def test_convention_loader(self, get_by_fqn):
        pattern = '.'.join(str(x) for x in (
            mock.Mock(name='first_mod'),
            mock.Mock(name='second_mod'),
            '%s_foobar'))
        loader = util.convention_loader(pattern)
        plugin = str(mock.Mock(name='Plugin'))
        result = loader(plugin)
        get_by_fqn.assert_called_once_with(pattern % plugin)
        self.assertEqual(get_by_fqn.return_value, result)

    def test_convention_loader_pattern_violations(self):
        for pattern in ('',
                        '%',
                        'foo.moo.nothing',
                        'foo.%',
                        'foo.%_blah',
                        'foo.%s_blah.%s',
                        'foo.%d_moo'):
            self.assertRaises(TypeError, lambda: util.convention_loader(pattern))

    def test_harness_loader_straight(self):
        loader = mock.Mock(name='Loader')
        callback = mock.Mock(name='Callback')
        harness = util.harness_loader(loader)(callback)
        name = mock.Mock(name='Plugin')
        args = [mock.Mock(name='Arg%d' % x) for x in xrange(3)]

        result = harness(name)
        loader.assert_called_once_with(name)
        callback.assert_called_once_with(loader.return_value)
        self.assertEqual(callback.return_value, result)

        loader.reset_mock()
        callback.reset_mock()
        result = harness(name, *args)
        loader.assert_called_once_with(name)
        callback.assert_called_once_with(*([loader.return_value] + args))
        self.assertEqual(callback.return_value, result)

    def test_harness_loader_decorator(self):
        loader = mock.Mock(name='Loader')
        @util.harness_loader(loader)
        def harness(target, *args):
            return target.called_with(*args)

        name = mock.Mock()
        result = harness(name, 1, 2, 3)
        loader.assert_called_once_with(name)
        loader.return_value.called_with.assert_called_once_with(1, 2, 3)
        self.assertEqual(loader.return_value.called_with.return_value, result)

