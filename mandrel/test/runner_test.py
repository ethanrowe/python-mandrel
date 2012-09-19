import unittest
import mock
import os
import sys
import mandrel
from mandrel import runner
from mandrel.test import utils

def scenario(*opts, **driver_opt):
    def wrapper(wrapped):
        def func(*a, **kw):
            values = sys.argv[:]
            libs = sys.path[:]
            del sys.argv[1:]
            sys.argv.extend(opts)
            if driver_opt.get('ensure_target', True):
                sys.argv.append(str(mock.Mock(name='MockTarget')))
            result = None
            try:
                with utils.bootstrap_scenario() as spec:
                    utils.refresh_bootstrapper()
                    result = wrapped(*(a + (spec[0],)), **kw)
            finally:
                del sys.argv[:]
                sys.argv[:] = values[:]
                sys.path[:] = libs[:]
            return result

        return func
    return wrapper

KNOWN_PATH = os.path.realpath('')

class TestRunner(unittest.TestCase):
    @scenario('-s', 'foo:bar:bah:', 'gloof', 'glof', 'floo', ensure_target=False)
    def testSearchPathSet(self, path):
        paths = [os.path.join(path, p) for p in ('foo', 'bar', 'bah')] + [path]
        result = runner.AbstractRunner().process_options()
        self.assertEqual(paths, list(mandrel.bootstrap.SEARCH_PATHS))
        self.assertEqual(('gloof', ['glof', 'floo']), result)

    @scenario('-p', 'blah')
    def testPrependSearchPath(self, path):
        runner.AbstractRunner().process_options()
        self.assertEqual(2, len(mandrel.bootstrap.SEARCH_PATHS))
        self.assertEqual(os.path.join(path, 'blah'), mandrel.bootstrap.SEARCH_PATHS[0])

    @scenario('-a', 'foof')
    def testAppendSearchPath(self, path):
        runner.AbstractRunner().process_options()
        self.assertEqual(2, len(mandrel.bootstrap.SEARCH_PATHS))
        self.assertEqual(os.path.join(path, 'foof'), mandrel.bootstrap.SEARCH_PATHS[-1])

    @scenario('-P', os.path.join(KNOWN_PATH, 'libbylib'))
    def testPrependModulePath(self, path):
        orig = len(sys.path)
        runner.AbstractRunner().process_options()
        self.assertEqual(orig + 1, len(sys.path))
        self.assertEqual(os.path.join(KNOWN_PATH, 'libbylib'), sys.path[0])

    @scenario('-A', os.path.join(KNOWN_PATH, 'florp'))
    def testAppendModulePath(self, path):
        orig = len(sys.path)
        runner.AbstractRunner().process_options()
        self.assertEqual(orig + 1, len(sys.path))
        self.assertEqual(os.path.join(KNOWN_PATH, 'florp'), sys.path[-1])

    @scenario('-l', 'loggity.logs')
    def testLogConfigBasenamePath(self, path):
        runner.AbstractRunner().process_options()
        self.assertEqual('loggity.logs', mandrel.bootstrap.LOGGING_CONFIG_BASENAME)

    @scenario()
    @mock.patch.object(runner.AbstractRunner, 'process_options')
    @mock.patch.object(runner.AbstractRunner, 'execute')
    def testOrderOfOperations(self, path, execute, process_options):
        mocks = [mock.Mock('positional%d' % x) for x in xrange(4)]
        target = mocks.pop(0)
        process_options.return_value = (target, mocks)
        runner.AbstractRunner().run()
        process_options.assert_called_once_with()
        execute.assert_called_once_with(target, mocks)

    @scenario()
    @mock.patch.object(runner.AbstractRunner, 'process_options')
    def testNotImplemented(self, path, process_options):
        process_options.return_value = ('a', [])
        self.assertRaises(NotImplementedError, runner.AbstractRunner().run)

    @scenario()
    def testImporting(self, _):
        obj = runner.AbstractRunner()
        with mock.patch('__builtin__.__import__') as importer:
            self.assertEqual(importer.return_value.bootstrap, obj.bootstrapper)
            importer.assert_called_once_with('mandrel.bootstrap')

    @mock.patch.object(runner.AbstractRunner, 'run')
    def testLaunch(self, run):
        runner.AbstractRunner.launch()
        run.assert_called_once_with()

    @mock.patch('mandrel.util.get_by_fqn')
    def testCallableRunner(self, get_by_fqn):
        target = str(mock.Mock(name='MockTarget'))
        opts = [str(mock.Mock(name='Arg%d' % x)) for x in xrange(3)]
        result = runner.CallableRunner().execute(target, opts)
        get_by_fqn.assert_called_once_with(target)
        get_by_fqn.return_value.assert_called_once_with(opts)
        self.assertEqual(get_by_fqn.return_value.return_value, result)

    @mock.patch('__builtin__.globals')
    @mock.patch('sys.argv', new=['foo', 'bar', 'bah'])
    @mock.patch('__builtin__.execfile')
    def testScriptRunner(self, mock_exec, mock_globals):
        target = str(mock.Mock(name='MockTarget'))
        opts = [str(mock.Mock(name='Arg%d' % x)) for x in xrange(3)]
        glb = {'foo': mock.Mock(), 'bar': mock.Mock(), '__file__': mock.Mock(), '__name__': mock.Mock()}
        mock_globals.side_effect = lambda: dict(glb)
        exp = dict(glb)
        exp['__file__'] = target
        exp['__name__'] = '__main__'

        result = runner.ScriptRunner().execute(target, opts)
        mock_exec.assert_called_once_with(target, exp)
        self.assertEqual(mock_exec.return_value, result)
        # Should add args at sys.argv[1:]
        self.assertEqual(['foo'] + opts, sys.argv)

    @mock.patch('mandrel.runner.ScriptRunner.launch')
    @mock.patch('mandrel.runner.CallableRunner.launch')
    def testLaunchFunctions(self, mock_callable, mock_script):
        runner.launch_callable()
        mock_callable.assert_called_once_with()
        self.assertEqual(0, len(mock_script.call_args_list))
        mock_callable.reset_mock()
        runner.launch_script()
        mock_script.assert_called_once_with()
        self.assertEqual(0, len(mock_callable.call_args_list))
