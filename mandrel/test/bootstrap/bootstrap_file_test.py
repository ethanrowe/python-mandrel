import contextlib
import os
import unittest
import mandrel.exception
from mandrel.test import utils

class TestBootstrapFile(utils.TestCase):
    def testNoFile(self):
        with utils.workdir(dir='~') as path:
            self.assertRaises(mandrel.exception.MissingBootstrapException, utils.refresh_bootstrapper)

    def testRootImmediate(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            utils.refresh_bootstrapper()
            self.assertEqual(spec[0], mandrel.bootstrap.ROOT_PATH)
            self.assertEqual(spec[1], mandrel.bootstrap.BOOTSTRAP_FILE)

    def testRootNested(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            with utils.tempdir(dir=spec[0]) as nested_a:
                with utils.workdir(dir=nested_a) as nested_b:
                    utils.refresh_bootstrapper()
                    self.assertEqual(spec[0], mandrel.bootstrap.ROOT_PATH)
                    self.assertEqual(spec[1], mandrel.bootstrap.BOOTSTRAP_FILE)

    def testFileEvaluation(self):
        with utils.bootstrap_scenario(text="bootstrap.EVAL_CHECK = bootstrap\nconfig.EVAL_CHECK = config") as spec:
            utils.refresh_bootstrapper()
            # We check that the bootstrap file is evaluated in a scope with:
            # - mandrel.bootstrap bound to local name "bootstrap"
            # - mandrel.config bound to local name "config"
            self.assertIs(mandrel.bootstrap, mandrel.bootstrap.EVAL_CHECK)
            self.assertIs(mandrel.config, mandrel.config.EVAL_CHECK)
            

    def testDefaultSearchPath(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            utils.refresh_bootstrapper()
            self.assertEqual([spec[0]], list(mandrel.bootstrap.SEARCH_PATHS))

    def testDefaultLoggingConfig(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            utils.refresh_bootstrapper()
            self.assertEqual('logging.cfg', mandrel.bootstrap.LOGGING_CONFIG_BASENAME)

