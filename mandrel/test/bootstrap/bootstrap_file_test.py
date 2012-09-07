import contextlib
import os
import unittest
import mandrel.exception
from mandrel.test import utils

class TestBootstrapFile(unittest.TestCase):
    def testNoFile(self):
        with utils.workdir(dir='~') as path:
            with self.assertRaises(mandrel.exception.MissingBootstrapException):
                utils.refresh_bootstrapper()

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
        with utils.bootstrap_scenario(text="bootstrap.EVAL_CHECK = bootstrap\n") as spec:
            utils.refresh_bootstrapper()
            self.assertIs(mandrel.bootstrap, mandrel.bootstrap.EVAL_CHECK)

    def testDefaultSearchPath(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            utils.refresh_bootstrapper()
            self.assertEqual([spec[0]], list(mandrel.bootstrap.SEARCH_PATHS))

    def testDefaultLoggingConfig(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            utils.refresh_bootstrapper()
            self.assertEqual('logging.cfg', mandrel.bootstrap.LOGGING_CONFIG_BASENAME)

