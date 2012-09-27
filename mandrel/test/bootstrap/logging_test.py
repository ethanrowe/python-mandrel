import unittest
import mock
import mandrel
from mandrel import exception
from mandrel.test import utils

class TestLoggingBootstrap(utils.TestCase):
    def testDefaultLoggingCallback(self):
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            self.assertIs(mandrel.bootstrap.initialize_simple_logging, mandrel.bootstrap.DEFAULT_LOGGING_CALLBACK)


    def testInitializeSimpleLogging(self):
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            with mock.patch('logging.basicConfig') as basic_config:
                with mock.patch('mandrel.bootstrap.DEFAULT_LOGGING_LEVEL') as default_level:
                    with mock.patch('mandrel.bootstrap.DEFAULT_LOGGING_FORMAT') as default_format:
                        with mock.patch('mandrel.bootstrap.DEFAULT_LOGGING_DATE_FORMAT') as default_date_fmt:
                            mandrel.bootstrap.initialize_simple_logging()
                            basic_config.assert_called_once_with(format=default_format, datefmt=default_date_fmt, level=default_level)


    @mock.patch('logging.INFO')
    def testSimpleLoggingDefaults(self, mock_info):
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            self.assertEqual(mock_info, mandrel.bootstrap.DEFAULT_LOGGING_LEVEL)
            self.assertEqual('%(asctime)s.%(msecs)04d #%(process)d - %(levelname)s %(name)s: %(message)s', mandrel.bootstrap.DEFAULT_LOGGING_FORMAT)
            self.assertEqual('%Y-%m-%dT%H:%M:%S', mandrel.bootstrap.DEFAULT_LOGGING_DATE_FORMAT)


    def testDisableExistingLoggers(self):
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            self.assertEqual(True, mandrel.bootstrap.DISABLE_EXISTING_LOGGERS)


    def testFindLoggingConfiguration(self):
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            mandrel.bootstrap.LOGGING_CONFIG_BASENAME = str(mock.Mock(name='MockLoggingConfigPath'))
            mandrel.bootstrap.SEARCH_PATHS = mock.Mock(name='MockSearchPaths')
            with mock.patch('mandrel.util.find_files') as find_files:
                path = mock.Mock(name='MockPath')
                find_files.return_value = iter([path])
                result = mandrel.bootstrap.find_logging_configuration()
                find_files.assert_called_once_with(mandrel.bootstrap.LOGGING_CONFIG_BASENAME, mandrel.bootstrap.SEARCH_PATHS, matches=1)
                self.assertEqual(path, result)

                find_files.reset_mock()
                find_files.return_value = iter([])
                self.assertRaises(exception.UnknownConfigurationException, lambda: mandrel.bootstrap.find_logging_configuration())


    @mock.patch('logging.config.fileConfig')
    def testConfigureLogging(self, file_config):
        callback = mock.Mock(name='DefaultLoggingCallback')
        disabled = mock.Mock(name='DisableExistingLogger')
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            mandrel.bootstrap.DEFAULT_LOGGING_CALLBACK = callback
            mandrel.bootstrap.DISABLE_EXISTING_LOGGERS = disabled
            with mock.patch('mandrel.bootstrap.find_logging_configuration') as finder:
                self.assertEqual(False, mandrel.bootstrap.logging_is_configured())
                path = str(mock.Mock(name='LoggingConfigPath'))
                finder.return_value = path
                mandrel.bootstrap.configure_logging()
                self.assertEqual(0, len(mandrel.bootstrap.DEFAULT_LOGGING_CALLBACK.call_args_list))
                file_config.assert_called_once_with(path, disable_existing_loggers=disabled)
                self.assertEqual(True, mandrel.bootstrap.logging_is_configured())

            utils.refresh_bootstrapper()
            mandrel.bootstrap.DEFAULT_LOGGING_CALLBACK = callback
            mandrel.bootstrap.DISABLE_EXISTING_LOGGERS = disabled
            file_config.reset_mock()
            with mock.patch('mandrel.bootstrap.find_logging_configuration') as finder:
                self.assertEqual(False, mandrel.bootstrap.logging_is_configured())
                def failure(*a, **k):
                    raise exception.UnknownConfigurationException
                finder.side_effect = failure
                mandrel.bootstrap.configure_logging()
                self.assertEqual(0, len(file_config.call_args_list))
                callback.assert_called_once_with()
                self.assertEqual(True, mandrel.bootstrap.logging_is_configured())


    @mock.patch('logging.getLogger')
    def testGetLogger(self, getLogger):
        name = str(mock.Mock(name='SomeLoggerName'))
        with utils.bootstrap_scenario() as spec:
            utils.refresh_bootstrapper()
            with mock.patch('mandrel.bootstrap.configure_logging') as configure_logging:
                with mock.patch('mandrel.bootstrap.logging_is_configured') as logging_is_configured:
                    logging_is_configured.return_value = False
                    result = mandrel.bootstrap.get_logger(name)
                    configure_logging.assert_called_once_with()
                    getLogger.assert_called_once_with(name)
                    self.assertEqual(getLogger.return_value, result)

                    configure_logging.reset_mock()
                    getLogger.reset_mock()
                    logging_is_configured.return_value = True
                    result = mandrel.bootstrap.get_logger(name)
                    self.assertEqual(0, len(configure_logging.call_args_list))
                    getLogger.assert_called_once_with(name)
                    self.assertEqual(getLogger.return_value, result)

