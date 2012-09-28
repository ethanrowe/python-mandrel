import unittest
import mock
from mandrel import config
from mandrel.config import helpers
from mandrel import util

def scenario(test):
    def func(self, *a, **k):
        cls = type('TestConfiguration', (config.Configuration,), {})
        with mock.patch.object(util, 'get_by_fqn'):
            with mock.patch.object(util, 'class_to_fqn'):
                return test(self, cls, *a, **k)
    return func

class TestLoaderHelpers(unittest.TestCase):
    def verify_class_set(self, conf, attr, key):
        value = mock.Mock()
        setattr(conf, attr, value)
        util.class_to_fqn.assert_called_once_with(value)
        self.assertEqual(util.class_to_fqn.return_value, conf.configuration[key])

        util.class_to_fqn.reset_mock()
        setattr(conf, attr, None)
        self.assertEqual(None, conf.configuration[key])

    @scenario
    def test_configurable_class_defined_no_default(self, cls):
        cls.foo = helpers.configurable_class('some_key')
        conf = cls({'some_key': 'some.great.Class', 'some_other_key': 'foo'})
        received = conf.foo
        util.get_by_fqn.assert_called_once_with('some.great.Class')
        self.assertEqual(util.get_by_fqn.return_value, received)
        self.verify_class_set(conf, 'foo', 'some_key')

    @scenario
    def test_configurable_class_defined_default(self, cls):
        cls.bar = helpers.configurable_class('this_one', 'that.great.thingy')
        conf = cls({'this_one': 'this.other.thing'})
        received = conf.bar
        util.get_by_fqn.assert_called_once_with('this.other.thing')
        self.assertEqual(util.get_by_fqn.return_value, received)
        self.verify_class_set(conf, 'bar', 'this_one')

    @scenario
    def test_configurable_class_no_key_default(self, cls):
        cls.bonk = helpers.configurable_class('no_go', 'special.default.thing')
        conf = cls({})
        received = conf.bonk
        util.get_by_fqn.assert_called_once_with('special.default.thing')
        self.assertEqual(util.get_by_fqn.return_value, received)
        self.verify_class_set(conf, 'bonk', 'no_go')

    @scenario
    def test_configurable_class_empty_string_default(self, cls):
        cls.pork = helpers.configurable_class('me', 'hey.this.awesomeness')
        conf = cls({'me': ''})
        received = conf.pork
        util.get_by_fqn.assert_called_once_with('hey.this.awesomeness')
        self.assertEqual(util.get_by_fqn.return_value, received)
        self.verify_class_set(conf, 'pork', 'me')

    @scenario
    def test_configurable_class_no_val_no_default(self, cls):
        cls.i_am_the_forty_seven_percent = helpers.configurable_class('good_ol_mitt')
        conf = cls({})
        self.assertEqual(None, conf.i_am_the_forty_seven_percent)
        self.verify_class_set(conf, 'i_am_the_forty_seven_percent', 'good_ol_mitt')

