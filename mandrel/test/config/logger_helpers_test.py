import unittest
import mock

from mandrel.config import core
from mandrel.config import helpers

def test_cls(bases=(core.Configuration,)):
    return type(str(mock.Mock(name='MockClass')), bases, {})

class TestLoggingConfigurationHelpers(unittest.TestCase):
    def test_named_logger(self):
        v = self.verify_named_logger
        v('some.base.name', (), 'some.base.name')
        v('ploopy.floo', ('blorp',), 'ploopy.floo.blorp')

    def verify_named_logger(self, logger_name, params, expected_name):
        cls = test_cls()
        cls.get_logger_name = helpers.named_logger(logger_name)
        self.assertEqual(expected_name, cls.get_logger_name(*params))

    def test_templated_name_logger(self):
        v = self.verify_templated_name_logger
        v('some.%s.special.template', 'very', (), 'some.very.special.template')
        v('another.special.%s.for', 'template', ('you',), 'another.special.template.for.you')

    def verify_templated_name_logger(self, template, name_const, params, expected_name):
        cls = test_cls()
        cls.NAME = name_const
        cls.get_logger_name = helpers.templated_name_logger(template)
        self.assertEqual(expected_name, cls.get_logger_name(*params))


    def test_name_chain_logger(self):
        cls = test_cls()
        cls.NAME = 'top'
        mid_cls_a = test_cls()
        mid_cls_a.NAME = 'mid_a'
        mid_cls_a.get_logger_name = helpers.name_chain_logger(cls)
        mid_cls_b = test_cls()
        mid_cls_b.NAME = 'mid_b'
        mid_cls_b.get_logger_name = helpers.name_chain_logger(cls)
        bot_cls_c = test_cls()
        bot_cls_c.NAME = 'bot_c'
        bot_cls_c.get_logger_name = helpers.name_chain_logger(mid_cls_a)
        bot_cls_d = test_cls()
        bot_cls_d.NAME = 'bot_d'
        bot_cls_d.get_logger_name = helpers.name_chain_logger(mid_cls_b)

        e = self.assertEqual
        e('top.mid_a', mid_cls_a.get_logger_name())
        e('top.mid_a.foo', mid_cls_a.get_logger_name('foo'))
        e('top.mid_a.bar', mid_cls_a.get_logger_name(name='bar'))
        e('top.mid_b', mid_cls_b.get_logger_name())
        e('top.mid_b.moo', mid_cls_b.get_logger_name('moo'))
        e('top.mid_a.bot_c', bot_cls_c.get_logger_name())
        e('top.mid_a.bot_c.blah', bot_cls_c.get_logger_name('blah'))
        e('top.mid_b.bot_d', bot_cls_d.get_logger_name())
        e('top.mid_b.bot_d.goo', bot_cls_d.get_logger_name('goo'))


    def test_hierarchical_logger(self):
        granny = test_cls()
        granny.NAME = 'granny'
        granny.get_logger_name = helpers.hierarchical_logger(granny)
        momma = test_cls((granny,))
        momma.NAME = 'momma'
        dadda = test_cls((granny,))
        dadda.NAME = 'dadda'
        kiddie = test_cls((momma,))
        kiddie.NAME = 'kiddie'
        e = self.assertEqual
        e('granny', granny.get_logger_name())
        e('granny.foo', granny.get_logger_name('foo'))
        e('granny.bar', granny.get_logger_name(name='bar'))
        e('granny.momma', momma.get_logger_name())
        e('granny.momma.foo', momma.get_logger_name('foo'))
        e('granny.momma.bar', momma.get_logger_name(name='bar'))
        e('granny.dadda', dadda.get_logger_name())
        e('granny.dadda.blah', dadda.get_logger_name('blah'))
        e('granny.dadda.moo', dadda.get_logger_name(name='moo'))
        e('granny.momma.kiddie', kiddie.get_logger_name())
        e('granny.momma.kiddie.aargh', kiddie.get_logger_name('aargh'))

