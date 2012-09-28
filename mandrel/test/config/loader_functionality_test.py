import contextlib
import unittest
import mock
import mandrel
from mandrel import exception
from mandrel.test import utils

def scenario(func):
    def wrapper(*a, **kw):
        with mock.patch('mandrel.bootstrap') as bootstrap:
            if hasattr(mandrel, 'config'):
                reload(mandrel.config.core)
                reload(mandrel.config)
            else:
                __import__('mandrel.config')
            return func(*a, **kw)
    return wrapper

class TestConfigLoaderFunctionality(unittest.TestCase):
    @scenario
    def testDefaultLoadersList(self):
        self.assertEqual([('yaml', mandrel.config.core.read_yaml_path)], mandrel.config.core.LOADERS)

    @scenario
    def testGetPossibleBasenames(self):
        a = mock.Mock(name='MockLoaderA')
        b = mock.Mock(name='MockLoaderB')
        a.extension = str(a.extension)
        b.extension = str(b.extension)
        name = str(mock.Mock(name='BaseName'))
        mandrel.config.core.LOADERS = [(a.extension, a), (b.extension, b)]
        
        self.assertEqual(['%s.%s' % (name, a.extension), '%s.%s' % (name, b.extension)],
                         mandrel.config.core.get_possible_basenames(name))

        mandrel.config.core.LOADERS.reverse()
        self.assertEqual(['%s.%s' % (name, b.extension), '%s.%s' % (name, a.extension)],
                         mandrel.config.core.get_possible_basenames(name))

        mandrel.config.core.LOADERS.reverse()
        self.assertEqual(['%s.%s' % (name, a.extension)],
                         mandrel.config.core.get_possible_basenames('%s.%s' % (name, a.extension)))
        self.assertEqual(['%s.%s' % (name, b.extension)],
                         mandrel.config.core.get_possible_basenames('%s.%s' % (name, b.extension)))


    @scenario
    def testFindConfigurationFiles(self):
        with mock.patch('mandrel.util.find_files') as find_files:
            with mock.patch('mandrel.config.core.get_possible_basenames') as get_possible_basenames:
                exts = [mock.Mock(name='Extension%d' % x) for x in xrange(3)]
                mandrel.config.core.LOADERS = [(ext, mock.Mock(name='Reader')) for ext in exts]
                mandrel.bootstrap.SEARCH_PATHS = mock.Mock()
                name = mock.Mock(name='FileBase')
                result = mandrel.config.core.find_configuration_files(name)
                get_possible_basenames.assert_called_once_with(name)
                find_files.assert_called_once_with(get_possible_basenames.return_value, mandrel.bootstrap.SEARCH_PATHS)
                self.assertEqual(find_files.return_value, result)

    @scenario
    def testFindConfigurationFileWithMatch(self):
        with mock.patch('mandrel.config.core.find_configuration_files') as find_configuration_files:
            paths = [mock.Mock(name='Path%d' % x) for x in xrange(10)]
            find_configuration_files.side_effect = lambda x: iter(paths)
            name = mock.Mock(name='SomeBase')
            result = mandrel.config.core.find_configuration_file(name)
            find_configuration_files.assert_called_once_with(name)
            self.assertEqual(paths[0], result)

    @scenario
    def testFindConfigurationFilesWithoutMatch(self):
        with mock.patch('mandrel.config.core.find_configuration_files') as find_configuration_files:
            find_configuration_files.side_effect = lambda x: iter([])
            self.assertRaises(exception.UnknownConfigurationException,
                              lambda: mandrel.config.core.find_configuration_file('foo'))

    @scenario
    def testGetLoader(self):
        exts = [str(mock.Mock(name='Extension%d' % x)) for x in xrange(3)]
        loaders = [mock.Mock(name='Loader%d' % x) for x in xrange(len(exts))]
        mandrel.config.core.LOADERS = zip(exts, loaders)

        for i in xrange(len(exts)):
            ext, loader = mandrel.config.core.LOADERS[i]
            path = '%s.%s' % (mock.Mock(name='someFile'), ext)
            result = mandrel.config.core.get_loader(path)
            self.assertEqual(loader, result)

        self.assertRaises(exception.UnknownConfigurationException,
                          lambda: mandrel.config.core.get_loader('foo.%s' % mock.Mock(name='NoLoader')))


    @scenario
    def testLoadConfigurationFile(self):
        with mock.patch('mandrel.config.core.get_loader') as getter:
            path = mock.Mock(name='SomeConfigurationPath')
            result = mandrel.config.core.load_configuration_file(path)
            getter.assert_called_once_with(path)
            getter.return_value.assert_called_once_with(path)
            self.assertEqual(getter.return_value.return_value, result)


    @scenario
    def testGetConfiguration(self):
        with mock.patch('mandrel.config.core.load_configuration_file') as loader:
            with mock.patch('mandrel.config.core.find_configuration_file') as finder:
                name = mock.Mock(name='SomeName')
                result = mandrel.config.core.get_configuration(name)
                finder.assert_called_once_with(name)
                loader.assert_called_once_with(finder.return_value)
                self.assertEqual(loader.return_value, result)

