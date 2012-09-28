import unittest
import mock
import mandrel.config
from mandrel.test import utils
from mandrel import exception

class TestConfigurationClass(utils.TestCase):
    @mock.patch('mandrel.config.core.get_configuration')
    def testLoadConfiguration(self, get_configuration):
        with mock.patch('mandrel.config.core.Configuration.NAME') as mock_name:
            result = mandrel.config.core.Configuration.load_configuration()
            get_configuration.assert_called_once_with(mock_name)
            self.assertEqual(get_configuration.return_value, result)

    @mock.patch('mandrel.bootstrap')
    def testGetLogger(self, bootstrap):
        mock_name = str(mock.Mock(name='MockConfigurationName'))
        with mock.patch('mandrel.config.core.Configuration.NAME', new=mock_name):
            result = mandrel.config.core.Configuration.get_logger()
            bootstrap.get_logger.assert_called_once_with(mock_name)
            self.assertEqual(bootstrap.get_logger.return_value, result)

            bootstrap.get_logger.reset_mock()
            result = mandrel.config.core.Configuration.get_logger('some.nested.name')
            bootstrap.get_logger.assert_called_once_with(mock_name + '.some.nested.name')
            self.assertEqual(bootstrap.get_logger.return_value, result)


    def testBasicAttributes(self):
        config = mock.Mock()
        c = mandrel.config.Configuration(config)
        self.assertEqual(config, c.configuration)
        self.assertEqual((), c.chain)

        chain = tuple(mock.Mock(name='Chain%d' % x) for x in xrange(3))
        c = mandrel.config.core.Configuration(config, *chain)
        self.assertEqual(config, c.configuration)
        self.assertEqual(chain, c.chain)

    def testConfigurationSetGet(self):
        config = mock.Mock(name='MockConfigDict')
        config.__getitem__ = mock.Mock()
        config.__setitem__ = mock.Mock()
        attr = mock.Mock(name='AttrKey')
        val = mock.Mock(name='Value')
        c = mandrel.config.core.Configuration(config)
        self.assertEqual(None, c.configuration_set(attr, val))
        config.__setitem__.assert_called_once_with(attr, val)
        result = c.configuration_get(attr)
        config.__getitem__.assert_called_once_with(attr)
        self.assertEqual(config.__getitem__.return_value, result)

    def testInstanceSetGet(self):
        c = mandrel.config.core.Configuration(mock.Mock())
        attr = str(mock.Mock(name='Attr'))
        val = mock.Mock(name='Value')
        self.assertEqual(None, c.instance_set(attr, val))
        self.assertEqual(val, c.instance_get(attr))
        self.assertEqual(val, c.__dict__[attr])


    def testInstanceVersusConfiguration(self):
        c = mandrel.config.core.Configuration({})
        attr = str(mock.Mock(name='Attr'))
        a = mock.Mock(name='A')
        b = mock.Mock(name='B')
        c.configuration_set(attr, a)
        self.assertEqual(a, getattr(c, attr))
        c.instance_set(attr, b)
        self.assertEqual(b, getattr(c, attr))
        self.assertEqual(b, c.instance_get(attr))
        self.assertEqual(a, c.configuration_get(attr))


    def testAttributeLookup(self):
        val = mock.Mock(name='Value')
        for getter in (lambda o: o.chained_get('foo'), lambda o: o.foo):
            self.assertRaises(AttributeError, lambda: getter(mandrel.config.core.Configuration({})))

            self.assertEqual(val, getter(mandrel.config.core.Configuration({'foo': val})))

            self.assertRaises(AttributeError, lambda: getter(mandrel.config.core.Configuration({}, object(), object())))

            good = mock.Mock(name='ChainMember')
            good.foo = val

            self.assertEqual(val, getter(mandrel.config.core.Configuration({'foo': val}, mock.Mock())))
            self.assertEqual(val, getter(mandrel.config.core.Configuration({}, good)))
            self.assertEqual(val, getter(mandrel.config.core.Configuration({}, object(), object(), good)))

    def testAttributeSet(self):
        a = mock.Mock(name='A')
        b = mock.Mock(name='B')
        c = mandrel.config.core.Configuration({}, object())

        c.foo = a
        self.assertEqual(a, c.configuration['foo'])

        c.foo = b
        self.assertEqual(b, c.configuration['foo'])

        c.blah = a
        self.assertEqual(a, c.configuration['blah'])

    def testAttributePropertySet(self):
        cls = type('AttributePropertyTestConfiguration', (mandrel.config.core.Configuration,), {})
        cls.foo = property(lambda self: self.configuration_get('blah'),
                           lambda self, val: self.configuration_set('blah', val))
        orig = mock.Mock(name='A')
        new = mock.Mock(name='B')
        x = cls({'blah': orig, 'foo': 'bar'})
        y = cls({'blah': orig})
        self.assertEqual(orig, x.foo)
        self.assertEqual(orig, y.foo)
        x.foo = new
        self.assertEqual(new, x.foo)
        self.assertEqual({'blah': new, 'foo': 'bar'}, x.configuration)
        self.assertEqual(orig, y.foo)

    @mock.patch('mandrel.config.core.Configuration.load_configuration')
    def testGetConfiguration(self, loader):
        c = mandrel.config.core.Configuration.get_configuration()
        self.assertEqual(loader.return_value, c.configuration)
        self.assertEqual((), c.chain)

        chain = tuple(mock.Mock() for x in xrange(5))
        c = mandrel.config.core.Configuration.get_configuration(*chain)
        self.assertEqual(loader.return_value, c.configuration)
        self.assertEqual(chain, c.chain)

    def testHotCopy(self):
        a = mandrel.config.core.Configuration({'foo': 'bar'})
        b = a.hot_copy()
        self.assertIs(type(a), type(b))
        self.assertEqual({}, b.configuration)
        self.assertEqual((a,), b.chain)

        c = type('ConfigSubclass', (mandrel.config.core.Configuration,), {})({})
        d = c.hot_copy()
        self.assertIs(type(c), type(d))


    def testForgivingConfiguration(self):
        self.assertEqual(True, issubclass(mandrel.config.core.ForgivingConfiguration, mandrel.config.core.Configuration))


    @mock.patch('mandrel.config.core.get_configuration')
    def testUnknownConfigurationExceptionHandling(self, get_configuration):
        def fail(*a, **b):
            raise exception.UnknownConfigurationException
        get_configuration.side_effect = fail
        
        class A(mandrel.config.core.Configuration):
            NAME = 'a_foo'

        class B(mandrel.config.core.ForgivingConfiguration):
            NAME = 'b_foo'

        self.assertRaises(exception.UnknownConfigurationException, A.load_configuration)

        b = B.load_configuration()
        self.assertEqual((('b_foo',), {}), get_configuration.call_args_list[-1])
        self.assertEqual({}, b)

