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

