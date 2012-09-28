import unittest
import mandrel.config

PUBLIC_NAMES = ['find_configuration_files',
                'find_configuration_file',
                'load_configuration_file',
                'get_configuration',
                'Configuration',
                'ForgivingConfiguration']

class TestPublicInterface(unittest.TestCase):
    def testEach(self):
        for name in PUBLIC_NAMES:
            self.assertEqual(id(getattr(mandrel.config.core, name)),
                             id(getattr(mandrel.config, name)))

    def testAll(self):
        self.assertEqual(sorted(PUBLIC_NAMES), sorted(mandrel.config.__all__))

