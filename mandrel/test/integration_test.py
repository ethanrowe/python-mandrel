import unittest
import os
import yaml
from mandrel.test import utils
import mandrel
from mandrel import config

BOOTSTRAP = """
bootstrap.SEARCH_PATHS.insert(0, 'specific_config')
bootstrap.DISABLE_EXISTING_LOGGERS = False
"""

def logger_conf(name, logfile):
    loggers = "[loggers]\nkeys=root,common%s,app%s\n\n" % (name, name)
    handlers = "[handlers]\nkeys=consoleHandler%s,fileHandler%s\n\n" % (name,name)
    formatters = "[formatters]\nkeys=simpleFormatter%s\n\n" % name
    root_logger = "[logger_root]\nlevel=DEBUG\nhandlers=consoleHandler%s\n\n" % name
    app_logger = "[logger_app%s]\nlevel=DEBUG\npropagate=0\nhandlers=fileHandler%s\nqualname=app%s\n\n" % (name, name, name)
    common_logger = "[logger_common%s]\nlevel=DEBUG\npropagate=0\nhandlers=fileHandler%s\nqualname=common%s\n\n" % (name, name, name)
    console = "[handler_consoleHandler%s]\nclass=StreamHandler\nlevel=DEBUG\nformatter=simpleFormatter%s\nargs=(sys.stderr,)\n\n" % (name, name) 
    handler = "[handler_fileHandler%s]\nclass=FileHandler\nlevel=DEBUG\nformatter=simpleFormatter%s\nargs=('%s',)\n\n" % (name, name, logfile)
    formatter = "[formatter_simpleFormatter" + name + "]\nformat=%(asctime)s - %(levelname)s - %(name)s - %(message)s\ndatefmt=\n\n"
    return loggers + handlers + formatters + root_logger + app_logger + common_logger + console + handler + formatter

def scenario(scenario_name, log=(), common=(), app=()):
    def decorator(wrapped):
        def func(*positionals, **keywords):
            with utils.bootstrap_scenario(text=BOOTSTRAP) as spec:
                path, bootstrap_file = spec
                os.mkdir('specific_config')

                for name, levels in (('common', common), ('app', app)):
                    for level in levels:
                        p = os.path.join(os.path.realpath(level), '%s%s.yaml' % (name, scenario_name))
                        with open(p, 'w') as stream:
                            yaml.dump({'%s_a' % name: 'a_%s' % level, '%s_b' % name: 'b_%s' % level}, stream)

                for level in log:
                    p = os.path.join(os.path.realpath(level), 'logging.cfg')
                    with open(p, 'w') as stream:
                        stream.write(logger_conf(scenario_name, '%s.log' % level))

                utils.refresh_bootstrapper()
                return wrapped(*positionals, **keywords)
        return func
    return decorator

def get_common(name, *chain):
    class Common(mandrel.config.Configuration):
        NAME = 'common%s' % name
    return Common.get_configuration(*chain)

def get_app(name, *chain):
    class App(mandrel.config.Configuration):
        NAME = 'app%s' % name
    return App.get_configuration(*chain)

class TestIntegratedScenarios(unittest.TestCase):
    @scenario('simple', log=('',), common=('',), app=('',))
    def testSimple(self):
        # In this case, all three configs are at the end of the search path.
        c = get_common('simple')
        a = get_app('simple')
        self.assertEqual('a_', c.common_a)
        self.assertEqual('b_', c.common_b)
        self.assertEqual('a_', a.app_a)
        self.assertEqual('b_', a.app_b)
        c.get_logger().info('common message')
        a.get_logger().info('app message')
        log = open('.log', 'r').read()
        self.assertTrue(' - commonsimple - common message' in log)
        self.assertTrue(' - appsimple - app message' in log)

    @scenario('specific', log=('','specific_config'), common=('', 'specific_config'), app=('', 'specific_config'))
    def testSpecific(self):
        # In this case, all three configs are in both levels of search path;
        # the specific_config one should win.
        c = get_common('specific')
        a = get_app('specific')
        self.assertEqual('a_specific_config', c.common_a)
        self.assertEqual('b_specific_config', c.common_b)
        self.assertEqual('a_specific_config', a.app_a)
        self.assertEqual('b_specific_config', a.app_b)
        c.get_logger().info('common message')
        a.get_logger().info('app message')
        log = open('specific_config.log', 'r').read()
        self.assertTrue(' - commonspecific - common message' in log)
        self.assertTrue(' - appspecific - app message' in log)

